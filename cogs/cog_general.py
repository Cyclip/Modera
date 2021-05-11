import discord
from discord.ext import commands
import config
import typing

from funcs.get_db import mongoClient


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

        self.dataDb = mongoClient.data
        self.serverSettings = self.dataDb.server_settings

    @commands.cooldown(1, 3, commands.BucketType.channel)
    @commands.command(
        description="Get all prefixes for this server", aliases=["pref", "prefixes"]
    )
    async def prefix(self, ctx):
        """
        Usage: `~prefix`
        """
        id = ctx.guild.id
        serverSettings = self.serverSettings.find_one({"id": id})

        if len(serverSettings) > 0:
            prefixes = serverSettings["prefixes"]
            prefStr = [f"{i+1}. `{j}`" for i, j in enumerate(prefixes)]

            embed = discord.Embed(
                title="Prefixes for Modera",
                color=config.uniColour,
            )

            embed.add_field(
                name="These are exclusive to this server.",
                value="\n".join(prefStr),
                inline=True,
            )

            await ctx.send(embed=embed)

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.command(description="Add a prefix", aliases=["addprefix", "addpref"])
    async def add_prefix(self, ctx, prefix: str):
        """
        Usage: `~add_prefix <prefix>`
        """
        if len(prefix) == 0:
            await ctx.send("Prefix is too short (min 1 char)")
            return
        elif len(prefix) > 6:
            await ctx.send("Prefix is too long (max 6 chars)")
            return

        prefixes = self.serverSettings.find_one({"id": ctx.guild.id})["prefixes"]
        if prefix in prefixes:
            return

        prefixes.append(prefix)

        key = {"id": ctx.guild.id}
        data = {"prefixes": prefixes}

        self.serverSettings.update_one(
            key,
            {
                "$set": data,
            },
            upsert=True,
        )

        await ctx.send("Updated prefixes!")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.command(
        description="Delete a prefix",
        aliases=["delprefix", "delpref", "removeprefix", "removepref"],
    )
    async def del_prefix(self, ctx, prefix: str):
        """
        Usage: `~del_prefix <prefix>`
        """
        if len(prefix) == 0:
            await ctx.send("Prefix is too short (min 1 char)")
            return
        elif len(prefix) > 6:
            await ctx.send("Prefix is too long (max 6 chars)")
            return

        prefixes = self.serverSettings.find_one({"id": ctx.guild.id})["prefixes"]
        if prefix not in prefixes:
            return await ctx.send(f"`{prefix}` isn't being used.")

        prefixes.remove(prefix)

        key = {"id": ctx.guild.id}
        data = {"prefixes": prefixes}

        self.serverSettings.update_one(
            key,
            {
                "$set": data,
            },
            upsert=True,
        )

        await ctx.send("Updated prefixes!")

    @commands.command(name="help", description="View the help menu")
    async def _help(self, ctx, module: typing.Optional[str] = ""):
        """
        Usage: `~help`
        """
        cogInfo = self.getCommandInfo()

        if module == "":
            # Show all cogs
            embed = discord.Embed(
                title=":question: Modera help menu",
                description="Type `~help <module>` to list commands for that module.\nType `~help <commands>` to show command usage.",
                color=config.uniColour,
            )

            for cog in cogInfo:
                embed.add_field(
                    name=f"{cog['name']} ({len(cog['commands'])} commands)",
                    value=f"`~help {cog['name']}` for help",
                    inline=True,
                )

        else:
            moduleNames = [
                i["name"].lower() for i in cogInfo if i["name"].lower() != "admin"
            ]
            found = False
            for i, n in enumerate(moduleNames):
                if module.lower() == moduleNames[i]:
                    embed = discord.Embed(
                        title=f"{module} commands".capitalize(),
                        description="Type `~help <command>` to show command usage",
                        color=config.uniColour,
                    )
                    cog = cogInfo[i]
                    if len(cog["commands"]) > 0:
                        for cmd in cog["commands"]:
                            val = (
                                cmd["help"]
                                if not (cmd["help"] is None or cmd["help"] == "")
                                else "No usage description"
                            )
                            if len(val) > 90:
                                val = val[:90] + "..."
                            if len(cmd["aliases"]) > 0:
                                displayAliases = [f"`{i}`" for i in cmd["aliases"]]
                                try:
                                    val += f"\nAliases: {', '.join(displayAliases)}"
                                except Exception:
                                    pass
                            embed.add_field(
                                name=cmd["name"],
                                value=val,
                            )
                    else:
                        embed.add_field(
                            name=f"{module} has no commands".capitalize(),
                            value="Some commands may be hidden.",
                        )
                    found = True
                    break

            if not found:
                commands, names = self.getCommands(cogInfo)
                try:
                    index = names.index(module.lower())
                    selected = commands[index]

                    embed = discord.Embed(
                        title=f"Help for {selected['name']}",
                        color=config.uniColour,
                    )

                    value2 = (
                        f"Aliases: {', '.join(selected['aliases'])}"
                        if len(selected["aliases"]) > 0
                        else "\u200b"
                    )

                    help_ = selected["help"]
                    if len(help_) > 256:
                        tmp = help_.split("\n")
                        help_ = tmp[0]
                        value2 += "\n" + "\n".join(tmp[1:])

                    embed.add_field(
                        name=selected["description"],
                        value="\u200b",
                        inline=False,
                    )
                    embed.add_field(name=help_, value=value2, inline=False)
                except IndexError:
                    embed.add_field(
                        name=f"{module} does not exist".capitalize(),
                        value="Some commands may be hidden.",
                    )

        # embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(
            value="Developed by [Cyclip](https://github.com/Cyclip/)",
            name="\u200B",
            inline=False,
        )
        await ctx.send(embed=embed)

    def getCommands(self, cogInfo):
        """
        Get all command info.
        Output example:
        [
            {
                "name": "commandName",
                "description": "commandDescription",
                "aliases": "aliases",
                "help": "help"
            },
            {
                "name": "commandName2",
                "description": "commandDescription2",
                "aliases": "aliases2",
                "help": "help2"
            },
            {
                "name": "commandName3",
                "description": "commandDescription3",
                "aliases": "aliases3",
                "help": "help3"
            }
        ]
        """
        commands = []
        names = []

        for cog in cogInfo:
            listCmds = cog["commands"]
            for cmd in listCmds:
                commands += [cmd]
                names.append(cmd["name"].lower())

        return commands, names

    def getCommandInfo(self):
        """
        Format:
        [
            {
                "name": cogName,
                "commands": [
                    {
                        "name": commandName,
                        "description": commandDescription,
                        "aliases": aliases
                    }
                ],
                "description": description
            }
        ]
        """
        cogInfo = []
        for cog in self.bot.cogs:
            commands = [
                {
                    "name": command.name,
                    "description": command.description,
                    "aliases": command.aliases,
                    "help": command.help,
                }
                for command in self.bot.get_cog(cog).get_commands()
            ]
            cogInfo.append(
                {
                    "name": cog,
                    "commands": commands,
                    "description": cog.__doc__,
                }
            )
        return cogInfo


def setup(bot):
    bot.add_cog(General(bot))
