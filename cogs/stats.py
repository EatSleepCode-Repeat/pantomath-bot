import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json
import os
import requests
import traceback

class StatusCog(commands.Cog, name="Status"):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xfc0322
        self.giveawayLoop.start()

    @tasks.loop(seconds=60.0)
    async def giveawayLoop(self):
        guild = self.bot.get_guild(718999389749641224)
        try:
            db = sqlite3.connect("main.db")
            cursor = db.cursor()

            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'stats.players'")
            result = cursor.fetchone()
            channelPlayers = guild.get_channel(int(result[0]))

            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'stats.version'")
            result = cursor.fetchone()
            channelVersion = guild.get_channel(int(result[0]))

            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'stats.status'")
            result = cursor.fetchone()
            channelStatus = guild.get_channel(int(result[0]))

            data = requests.get("https://mcstatus.snowdev.com.br/api/query/178.32.109.145").json()

            if data["Online"]:
                playersOnline = data["PlayersOnline"]
                playersMax = data["MaxPlayers"]
                version = "1.8 - 1.15"
                status = data["Online"]
                print(playersOnline, playersMax, version, status)

                await channelStatus.edit(name="Status: Online")
                await channelVersion.edit(name=f"Current version: {version}")
                await channelPlayers.edit(name=f"Online: {playersOnline} / {playersMax}")
            else:
                await channelStatus.edit(name="Status: Offline")
                await channelVersion.edit(name=f"Current version: {version}")
                await channelPlayers.edit(name=f"Online: N/A / N/A")

        except Exception as e:
            print(traceback.format_exc())


def setup(bot):
    bot.add_cog(StatusCog(bot))
    print("Status is loaded")
