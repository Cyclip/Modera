import discord
from discord.ext import commands, tasks
import typing
import difflib
import hashlib
import re
import asyncio

from funcs.get_db import mongoClient
from funcs import comment_analysis
import config


class Filtering(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.dataDb = mongoClient.data
        self.queue = self.dataDb.queue
        self.serverSettings = self.dataDb.server_settings

        self.handle_queue.start()

    def cog_unload(self):
        self.handle_queue.cancel()

    @commands.cooldown(4, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.command(
        description="Toggle deleting flagged comments",
        aliases=["delete", "delcomments"],
    )
    async def deleteCommments(self, ctx, newVal: str):
        """
        Usage: `~deleteComments <on/off>`
        """
        key = {"id": ctx.guild.id}
        data = {"deleteComments": True if newVal == "on" else False}
        self.serverSettings.update(key, {"$set": data}, upsert=True)
        await ctx.send("Updated settings!")

    @commands.cooldown(2, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.command(
        description="Get attribute information",
        aliases=["attrib", "attr", "getattr", "getattrib"],
    )
    async def attribute(self, ctx, type_: str):
        validTypes = list(config.attributes.keys())
        if type_ not in validTypes:
            msg = f"`{type_}` **is not a valid text filtering type.**\nValid types: {','.join([f'`{i}`' for i in validTypes])}"
            closest = difflib.get_close_matches(type_, validTypes)
            if len(closest) > 0:
                msg += f"\nMaybe you meant `{closest[0]}`?"
            return await ctx.send(msg)

        key = {"id": ctx.guild.id}
        embed = self.get_attribute_details(key, type_)

        await ctx.send(embed=embed)

    @commands.cooldown(2, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.command(description="Toggle certain text filtering")
    async def text(
        self,
        ctx,
        type_: str,
        setting: typing.Optional[str] = "",
        newVal: typing.Optional[str] = "",
    ):
        """
        Usage: `~text <filtering type> [setting] [new value]`
        Get/set a specific text filtering attribute.

        __Examples:__
        Input: `~text toxicity`
        Output: ```<Toxicity explanation>
        Enabled: True
        Threshold: 70
        ```

        Input: `~text toxicity enabled on`
        Output: `Toxicity filtering has been enabled.`

        __Available text attributes:__
        • `toxicity`
        • `abusive`
        • `identity_attack`
        • `insults`
        • `profanity`
        • `threats`
        • `sexual`
        • `flirtation`
        • `incoherency`
        • `inflammatory`
        """
        validTypes = list(config.attributes.keys())
        if type_ not in validTypes:
            msg = f"`{type_}` **is not a valid text filtering type.**\nValid types: {','.join([f'`{i}`' for i in validTypes])}"
            closest = difflib.get_close_matches(type_, validTypes)
            if len(closest) > 0:
                msg += f"\nMaybe you meant `{closest[0]}`?"
            return await ctx.send(msg)

        key = {"id": ctx.guild.id}

        if setting == "":
            embed = self.get_attribute_details(key, type_)

            await ctx.send(embed=embed)

        else:
            if newVal == "":
                return await ctx.send(
                    "Missing argument 'new value'\nExample: `~text toxicity status on`"
                )

            server = self.serverSettings.find_one(key)
            val = server[type_ + "Filtering"]
            if newVal == "on":
                newVal = True
            elif newVal == "off":
                newVal = False
            elif newVal.isdigit():
                range_ = config.attributes[type_]["settings"][setting]["range"]
                if newVal < range_[0]:
                    return await ctx.send(
                        f"Value is too low (must be {range_[0]} or above)"
                    )
                elif newVal > range_[1]:
                    return await ctx.send(
                        f"Value is too high (must be {range_[1]}) or below"
                    )
                newVal = int(newVal) / 100

            val[setting] = newVal
            server[type_ + "Filtering"] = val

            self.serverSettings.update_one(
                key,
                {
                    "$set": server,
                },
                upsert=True,
            )

            await ctx.send(f"`{type_}` has been {'enabled' if newVal else 'disabled'}.")

    def get_attribute_details(self, key, type_):
        selected = config.attributes[type_]
        print(selected)

        embed = discord.Embed(
            title=f"{type_} text attribute",
            description=selected["description"] + "\nSettings:",
            color=config.uniColour,
        )

        for setting_, details in selected["settings"].items():
            if details["restrict"] == "values":
                tmp = ", ".join([f"`{i}`" for i in details["values"]])
                val = f"Options: {tmp}"
            elif details["restrict"] == "range":
                val = f"Range: {details['range'][0]} to {details['range'][1]}"
            embed.add_field(
                name=setting_,
                value=val,
                inline=True,
            )

        currentVal = self.serverSettings.find_one(key)[type_ + "Filtering"]
        currentValFormatted = "\n".join(
            [f"**{i}**: {j}" for i, j in currentVal.items()]
        )

        embed.add_field(
            name=f"Current server settings for {type_}",
            value=currentValFormatted,
            inline=False,
        )

        return embed

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Add to queue
        if ctx.author.bot or ctx.content.startswith("~") or ctx.guild.id is None:
            return
        msg, id = ctx.content, f"{ctx.channel.id}/{ctx.id}"
        if len(msg) > 2 and not msg.startswith("!"):
            key = {"id": id}
            data = {"msg": msg}

            self.queue.update(key, {"$set": data}, upsert=True)
            print(f"Added {id} to queue")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (user.id != self.bot.user.id) and (str(reaction.emoji) == "⚠️"):
            if reaction.message.author == self.bot.user:
                logChannelID = self.serverSettings.find_one(
                    {"id": reaction.message.guild.id}
                )["logTo"]
                logChannel = await self.bot.fetch_channel(logChannelID)

                if reaction.message.channel == logChannel:
                    try:
                        originalEmbed = reaction.message.embeds[0]
                        embedInfo = originalEmbed.to_dict()
                        messages, filters, id_ = self.evaluate_violation_embed(
                            embedInfo
                        )
                        if not self.verify_embed(embedInfo):
                            return
                        newEmbed = self.add_warning_title(embedInfo, id_)

                        key = {"id": id_}
                        data = {
                            "messages": messages,
                            "filters": filters,
                            "serverID": reaction.message.guild.id,
                        }

                        self.dataDb.flagged_messages.update(
                            key,
                            {
                                "$set": data,
                            },
                            upsert=True,
                        )

                        await reaction.message.edit(
                            embed=discord.Embed.from_dict(newEmbed)
                        )
                        await reaction.message.clear_reactions()
                        print(key, data)
                    except Exception as e:
                        reaction.message.channel.send(
                            f"There was an error while reporting message"
                        )
                        raise e

    def evaluate_violation_embed(self, info):
        msgsVals = next(i for i in info["fields"] if i["name"] == "Messages")
        filtersVals = next(i for i in info["fields"] if i["name"] == "Flagged filters")
        msgs = re.findall("`(.*)`", msgsVals["value"])
        filters = filtersVals["value"].split(", ")
        id_ = hashlib.sha256((".".join(msgs) + ".".join(filters)).encode()).hexdigest()
        return msgs, filters, id_

    def add_warning_title(self, info, id_):
        info["title"] = "⚠️ " + info["title"]
        info["description"] += f"\nReport ID: {id_}"
        info["color"] = 14177041
        return info

    def verify_embed(self, info):
        return not info["title"].startswith("⚠️")

    @tasks.loop(seconds=2)
    async def handle_queue(self):
        # Get queue
        queue = self.queue.find()

        # Build single str
        queueStr = "\n".join([f"{i['id']}: {i['msg']}" for i in queue])
        if len(queueStr) == 0:
            return

        print(f"QUEUE: {queueStr}\n")

        # Send for analysis
        results = await self.analyse(queueStr)

        # Handle each message according to server settings
        self.settingsCache = {}
        handledMsgs = []
        serverData = {}
        for msg, data in results.items():
            if msg in handledMsgs or msg is False:
                continue
            else:
                handledMsgs.append(msg)

            if msg.guild not in serverData.keys():
                serverData[msg.guild] = {}

            # Get server settings
            violations = []
            try:
                serverSettings = self.get_server_settings(msg.guild.id)
            except:
                # dms
                continue
            for filterType, options in serverSettings.items():
                # For each filter type...
                if not filterType.endswith("Filtering") or not options["enabled"]:
                    continue

                # May or may not have allow_nsfw option
                try:
                    if options["allow_nsfw"] and msg.channel.nsfw:
                        continue
                except Exception:
                    pass

                # Check if it meets Threshold
                threshold = options["threshold"] / 100
                try:
                    val = data[config.attributeConv[filterType]]
                except Exception:
                    continue
                if val >= threshold:
                    # Meets or exceeds
                    violations.append(filterType)

            if msg.author not in serverData[msg.guild].keys():
                serverData[msg.guild][msg.author] = {
                    "msg": [msg if len(violations) > 0 else []],
                    "violations": violations,
                }
            else:
                serverData[msg.guild][msg.author]["msg"].append(msg)
                serverData[msg.guild][msg.author]["violations"].extend(violations)
                serverData[msg.guild][msg.author]["violations"] = list(
                    dict.fromkeys(serverData[msg.guild][msg.author]["violations"])
                )

        await self.handle_violations(serverData)

        # Clear queue
        self.queue.remove({})
        print("Cleared queue")

    async def handle_punishments(self, serverID, user, messages, violations):
        punishmentSettings = self.get_server_settings(serverID)["punishment"]
        ctx = messages[0]

        for violation in violations:
            actions = punishmentSettings[violation]
            for action in actions:
                print(f"Action {action}")
                if action["type"] == "ban":
                    await ctx.guild.ban(
                        user, reason=self.format_reason(messages, action)
                    )
                elif action["type"] == "kick":
                    await ctx.guild.kick(
                        user, reason=self.format_reason(messages, action)
                    )
                elif action["type"] == "mute":
                    role = discord.utils.get(server.roles, name="muted")
                    loop = asyncio.get_event_loop()
                    loop.create_task(
                        self.mute_user(ctx.author, ctx.guild, role, action)
                    )
                elif action["type"] == "addRole":
                    role = discord.utils.get(server.roles, name=action["rolename"])
                    await ctx.author.add_roles(role)
                elif action["type"] == "removeRole":
                    role = discord.utils.get(server.roles, name=action["rolename"])
                    await ctx.author.remove_roles(role)
                elif action["type"] == "warn":
                    pass
                elif action["type"] == "dm":
                    reason = self.format_reason(messages, action)
                    msg = f"Message from {ctx.guild.name}:\n```{reason}```"
                    if action["user"] == 0:
                        await ctx.author.send(msg)
                    else:
                        await self.bot.get_user(action["user"]).send(msg)

    def format_reason(self, messages, action):
        try:
            reason = action["reason"]
        except:
            reason = action["msg"]
        reason = reason.replace(
            "{MESSAGE}", ", ".join([f"'{i.content[:50]}'" for i in messages])
        )
        try:
            reason = reason.replace("{REASON}", action["reason"])
        except:
            pass
        reason = reason.replace(
            "{JUMP}",
            ", ".join([f"[Jump {i}]({j.jump_url})" for i, j in enumerate(messages)]),
        )
        return reason

    async def mute_user(self, guild, user, role, action):
        await user.add_roles(role)
        reason = self.format_reason(action)
        user.send(
            f"You have been muted from {guild.name} for {action['duration']} seconds:\n```{reason}```"
        )
        await asyncio.sleep(action["duration"])
        await user.remove_roles(role)

    async def handle_violations(self, data):
        """
        {
            server: {
                user: {
                    "msg": [1, 2],
                    "violations": [1, 2]
                }
            }
        }
        """
        print("Handling violations with", data)

        for server, users in data.items():
            serverSettings = self.get_server_settings(server.id)
            print(f"Doing {server.id}")

            for user, details in users.items():
                print(f"Handling {user.name} - {details}")
                if len(details["violations"]) == 0:
                    print(f"No violations ({details['violations']})")
                    continue

                # Punish
                await self.handle_punishments(
                    server.id, user, details["msg"], details["violations"]
                )

                msgs = [i for i in details["msg"] if not isinstance(i, list)]

                # Log to channel
                channel = await self.bot.fetch_channel(serverSettings["logTo"])
                violatedChannels = list(
                    dict.fromkeys([f"<#{i.channel.id}>" for i in msgs])
                )

                embed = discord.Embed(
                    title=f"Flagged messages for {user.name}#{user.discriminator}",
                    description=f"User ID: {user.id}",
                    color=config.uniColour,
                )

                embed.add_field(
                    name="Messages",
                    value="\n".join(
                        [f"`{i.content}` - [Jump]({i.jump_url})" for i in msgs]
                    ),
                    inline=False,
                )

                embed.add_field(
                    name="Flagged filters",
                    value=", ".join(details["violations"]),
                    inline=False,
                )

                embed.add_field(
                    name="Channels",
                    value="\n".join(violatedChannels),
                    inline=False,
                )

                embed.add_field(
                    name="\u200b",
                    value="React with :warning: to report a false positive",
                    inline=False,
                )

                embed.set_thumbnail(url=user.avatar_url)

                try:
                    embedMsg = await channel.send(embed=embed)

                    await embedMsg.add_reaction("⚠️")
                except:
                    return

                if serverSettings["deleteComments"]:
                    for msg in msgs:
                        try:
                            await msg.delete()
                        except Exception:
                            continue

    async def analyse(self, queueStr):
        resp = comment_analysis.request(queueStr)
        return await self.format_analysis(resp, queueStr)

    async def format_analysis(self, resp, queueStr):
        queueStr = [
            await self.handle_link(i.split(":")[0]) for i in queueStr.split("\n")
        ]
        data = dict([(i, {}) for i in queueStr])

        for attr, scores in resp.items():
            for msgid, scoreData in enumerate(scores["spanScores"]):
                try:
                    data[queueStr[msgid]][attr] = scoreData["score"]["value"]
                except Exception:
                    pass
        return data

    async def handle_link(self, link):
        link = [int(i) for i in link.split("/")]

        try:
            channel = await self.bot.fetch_channel(link[0])
            return await channel.fetch_message(link[1])
        except Exception:
            return False

    def get_server_settings(self, _id):
        if _id not in self.settingsCache.keys():
            settings = self.serverSettings.find_one({"id": _id})
            self.settingsCache[_id] = settings

        return self.settingsCache[_id]


def setup(bot):
    bot.add_cog(Filtering(bot))
