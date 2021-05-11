import discord
from discord.ext import commands
import config
import typing

from funcs.get_db import mongoClient


class Incidents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.dataDb = mongoClient.data
        self.queue = self.dataDb.queue
        self.serverSettings = self.dataDb.server_settings

    @commands.command(aliases=["logTo"], description="Log all incidents to this channel.")
    async def log(self, ctx, channel: typing.Optional[discord.TextChannel]):
        """
        Usage: `~log <#channel>`
        """
        key = {"id": ctx.guild.id}

        if channel:
            data = {"logTo": channel.id}

            self.serverSettings.update(
                key,
                {
                    "$set": data
                },
                upsert=True
            )

            embed = discord.Embed(
                title="Now logging incidents to this channel.",
                description="You may change it via `~log`",
                color=config.uniColour,
            )
        else:
            current = self.serverSettings.find_one(key)["logTo"]
            channel_ = await self.bot.fetch_channel(current)
            print(channel)
            embed = discord.Embed(
                title=f"Currently logging to #{channel_.name}",
                color=config.uniColour,
            )
            channel = ctx

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Incidents(bot))
