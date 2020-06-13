import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json
import os

class PollCog(commands.Cog, name="Poll"):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xfc0322

    def get_perms(self, user):
        db = sqlite3.connect("main.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT role_id, perm FROM rolePerms")
        results = cursor.fetchall()

        perms = []
        if results is not None:
            for role in user.roles:
                for id, perm in results:
                    if str(role.id) == id and perm not in perms:
                        perms.append(perm)

        return perms

    @commands.command()
    async def poll(self, ctx, *, question):
        if "poll.create" in self.get_perms(ctx.author):
            db = sqlite3.connect("main.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'poll.output'")
            result = cursor.fetchone()

            channel = ctx.guild.get_channel(int(result[0]))

            embed = discord.Embed(color=self.color, title="New poll!", description=question)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

            msg = await channel.send(embed=embed)

            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
        else:
            await ctx.send("You do not have the requed permissions to run this command.")



def setup(bot):
    bot.add_cog(PollCog(bot))
    print("Poll is loaded")
