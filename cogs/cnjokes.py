import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json
import os
import requests

class CnjokesCog(commands.Cog, name="CNJokes"):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xfc0322

    @commands.command()
    async def cnjoke(self, ctx):
        response = requests.get("https://api.chucknorris.io/jokes/random").json()["value"]
        await ctx.send(response)



def setup(bot):
    bot.add_cog(CnjokesCog(bot))
    print("cnjokes is loaded")
