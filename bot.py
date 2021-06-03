import discord
from discord.ext import commands
import traceback
import datetime
import os
from dotenv import load_dotenv
import asyncio

import config
import decorators
from funcs.get_db import mongoClient


class Modera:
    """
    Main class for Modera
    Usage:
        Modera(str token, str prefix, str description)
    """

    def __init__(self, token, prefix, description, intents):
        self.token = token
        self.prefix = prefix
        self.bot = commands.Bot(
            command_prefix=self.get_prefix,
            description=description,
            case_insensitive=True,
            intents=intents,
        )
        self.loadedCogs = []  # For loading and unloading cogs

        self.errorsShowHelp = [commands.MissingRequiredArgument]

        self.loadCogs()
        self.addCommands()
        self.addEvents()

    def addCommands(self):
        """
        Internal commands in the main class
        """

        @commands.check(decorators.owner_required)
        @self.bot.command(pass_context=True)
        async def reload(ctx):
            self.unloadCogs()
            self.loadCogs()
            embed = discord.Embed(
                title="Reloaded cogs",
                description=f"{len(self.loadedCogs)} cogs loaded",
                color=0x00FF29,
            )
            await ctx.send(embed=embed)

    def addEvents(self):
        """
        All events are handled here
        """

        @self.bot.event
        async def on_command_error(ctx, error):
            isInESH = False
            for esh in self.errorsShowHelp:
                if isinstance(error, esh):
                    e = await self.showHelp()
                    await ctx.send(embed=e)
                    isInESH = True
                    break

            if not isInESH:
                if isinstance(error, commands.CommandOnCooldown):
                    # Cooldown error
                    embed = discord.Embed(
                        title=f"You need to wait {round(error.retry_after, 1)}s before using this command again",
                        color=0xFF0000,
                    )
                    await ctx.send(embed=embed, delete_after=10)
                    asyncio.sleep(config.cooldownCooldown)

            raise error  # So errors show up in console

        @self.bot.event
        async def on_ready():
            await self.setPresence(config.status)

        @self.bot.event
        async def on_guild_join(ctx):
            self.setup_server_settings(ctx)
            for channel in ctx.text_channels:
                if channel.permissions_for(ctx.me).send_messages:
                    try:
                        embed = discord.Embed(
                            title="Modera has been added",
                            description="The bot is currently in beta.",
                            color=0x2555C1,
                        )
                        await channel.send(embed=embed)
                    except Exception:
                        pass
                    break

    async def setPresence(self, text):
        await self.bot.change_presence(
            activity=discord.Game(name=text), status=discord.Status.dnd
        )

    async def showHelp(self, title="Modera help"):
        embed = discord.Embed(
            title=title, description=f"Use {self.prefix}help for help with commands."
        )
        return embed

    def get_prefix(self, bot, msg):
        id = msg.guild.id
        return serverSettings.find_one({"id": id})["prefixes"]

    def setup_server_settings(self, ctx):
        key = {"id": ctx.id}
        data = {
            "id": ctx.id,
            "prefixes": [
                "~",
                "m~",
            ],
            "deleteComments": True,
            "logTo": ctx.text_channels[0].id,
            "toxicityFiltering": {"enabled": False, "threshold": 80},
            "abusiveFiltering": {"enabled": True, "threshold": 60},
            "identity_attackFiltering": {"enabled": True, "threshold": 85},
            "insultsFiltering": {"enabled": True, "threshold": 90},
            "profanityFiltering": {"enabled": False, "threshold": 70},
            "threatsFiltering": {"enabled": True, "threshold": 70},
            "sexualFiltering": {"enabled": True, "threshold": 80, "allow_nsfw": False},
            "flirtationFiltering": {
                "enabled": True,
                "threshold": 85,
                "allow_nsfw": False,
            },
            "incoherencyFiltering": {"enabled": False, "threshold": 90},
            "inflammatoryFiltering": {"enabled": False, "threshold": 80},
            "punishment": {
                "toxicityFiltering": [],
                "abusiveFiltering": [],
                "identity_attackFiltering": [],
                "insultsFiltering": [],
                "profanityFiltering": [],
                "threatsFiltering": [],
                "sexualFiltering": [],
                "flirtationFiltering": [],
                "incoherencyFiltering": [],
                "inflammatoryFiltering": [],
            },
        }
        serverSettings.update_one(
            key,
            {
                "$set": data,
            },
            upsert=True,
        )

    def loadCogs(self, ignoreAdmin=False):
        """
        Load all cogs in ./cogs which start with "cog_"
        """
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") and cog.startswith("cog_"):
                if (ignoreAdmin and cog != "cog_admin.py") or not ignoreAdmin:
                    try:
                        cog = f"cogs.{cog.replace('.py', '')}"
                        self.bot.load_extension(cog)
                        self.loadedCogs.append(cog)
                        print(f"Loaded {cog}")
                    except Exception:
                        print(f"{cog} failed to load")
                        print(traceback.format_exc())

    def unloadCogs(self, ignoreAdmin=False):
        """
        Unload all cogs in self.loadedCogs
        """
        for cogName in self.loadedCogs:
            self.bot.unload_extension(cogName)
            print(f"Unloaded {cogName}")

        self.loadedCogs = []

    def start(self):
        self.bot.run(self.token)


if __name__ == "__main__":
    load_dotenv()

    dataDb = mongoClient.data
    serverSettings = dataDb.server_settings

    intents = discord.Intents.default()
    intents.messages = True
    intents.reactions = True

    try:
        ssb = Modera(
            os.getenv("DISCORD_TOKEN"), config.prefix, config.description, intents
        )
        ssb.start()
    except Exception:
        now = datetime.datetime.now()
        with open(
            f"crashes/{now.day}-{now.month}-{now.year} {now.hour}-{now.minute}-{now.second}.log",
            "w",
        ) as f:
            err = traceback.format_exc()
            f.write(err)
            print(err)
