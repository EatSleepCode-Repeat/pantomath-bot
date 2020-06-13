import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json
import os
import random
import traceback
import sys

class GiveawayCog(commands.Cog, name="Giveaway"):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xfc0322
        self.giveawayLoop.start()

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
    async def giveaway(self, ctx):
        if "giveaway.create" in self.get_perms(ctx.author):
            embed = discord.Embed(color=self.color, title="Welcome to Giveaway Processing", description="Please type the title of the Giveaway.")
            embed.set_footer(text="The form times out after 60 seconds.")

            message = await ctx.send(embed=embed)

            def check(message):
                return message.channel == ctx.channel and message.author == ctx.author

            try:
                msg = await self.bot.wait_for('message', timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Form timed out.")
                return
            else:
                await msg.delete()
                title = msg.content

            #===============================================================================================0

            embed = discord.Embed(color=self.color, title="Welcome to Giveaway Processing", description="Please type the description of the Giveaway.")
            embed.set_footer(text="The form times out after 60 seconds.")

            await message.edit(embed=embed)

            def check(message):
                return message.channel == ctx.channel and message.author == ctx.author

            try:
                msg = await self.bot.wait_for('message', timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Form timed out.")
                return
            else:
                await msg.delete()
                text = msg.content


                # ===================================================================

            embed = discord.Embed(color=self.color, title="Giveaway Processing", description="Please type the amount of days you want the giveawey to last.")
            embed.set_footer(text="The form times out after 60 seconds.")

            await message.edit(embed=embed)

            while True:
                try:
                    msg = await self.bot.wait_for('message', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("Form timed out.")
                    return
                else:
                    await msg.delete(delay=1)
                    try:
                        time = int(msg.content)
                    except:
                        await ctx.send("Invalid number.", delete_after=2)
                        continue
                    else:
                        break

            #===============================================================================================0

            embed = discord.Embed(color=self.color, title="Giveaway Processing", description="Please type the amount of winners.")
            embed.set_footer(text="The form times out after 60 seconds.")

            await message.edit(embed=embed)

            while True:
                try:
                    msg = await self.bot.wait_for('message', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("Form timed out.")
                    return
                else:
                    await msg.delete(delay=1)
                    try:
                        winners = int(msg.content)
                    except:
                        await ctx.send("Invalid number.", delete_after=2)
                        continue
                    else:
                        break



            #==============================================================================

            embed = discord.Embed(color=self.color, title="Giveaway Processing", description="Add the reaction of the giveawey.")
            embed.set_footer(text="The form times out after 60 seconds.")

            await message.edit(embed=embed)

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and user.bot == False

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Form timed out.")
                return
            else:
                #reaction = str(reaction)
                pass

                await message.clear_reactions()
                await message.add_reaction("📨")

                #==============================================================================

            db = sqlite3.connect("main.db")
            cursor = db.cursor()

            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'giveaway.output'")
            results = cursor.fetchone()
            channel = ctx.guild.get_channel(int(results[0]))

            now = datetime.datetime.now()
            delta = datetime.timedelta(days=time)

            now_with_delta = now + delta

            embed = discord.Embed(color=self.color, title=title,
                                  description=f"{text}\nEnds: {now_with_delta.strftime('%x %X')} Winners: {winners}")
            msg = await channel.send(embed=embed)

            await msg.add_reaction(reaction)


            stamp = now_with_delta.timestamp()

            sql = ("INSERT INTO giveaway(message_id, time, winners) VALUES (?,?,?)")
            val = (msg.id, stamp, winners)

            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("You do not have the required permissions to run this command.")

    @tasks.loop(seconds=10.0)
    async def giveawayLoop(self):
        try:
            db = sqlite3.connect("main.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT message_id, time, winners FROM giveaway")
            results = cursor.fetchall()

            for result in results:
                now = datetime.datetime.now()
                stamp = now.timestamp()
                if float(result[1]) - stamp <= 0:
                    cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'giveaway.output'")
                    channel = cursor.fetchone()

                    guild = self.bot.get_guild(718999389749641224)
                    channel = guild.get_channel(int(channel[0]))
                    message = await channel.fetch_message(id=int(result[0]))
                    reaction = message.reactions[0]
                    users = await reaction.users().flatten()
                    winners = []
                    for i in range(result[2]):
                        try:
                            user = random.choice(users)
                            users.pop(users.index(user))
                            if not user.bot:
                                winners.append(user)
                            else:
                                users.pop(users.index(user))
                                user = random.choice(users)
                                users.pop(users.index(user))
                                winners.append(user)
                        except IndexError:
                            break

                    for win in winners:
                        await channel.send(f"Congratulations! {win.mention} you have won the giveaway! \n{message.jump_url}")

                    cursor.execute(f"DELETE from giveaway WHERE message_id = '{result[0]}'")
                    db.commit()
                    cursor.close()
                    db.close()

        except Exception as e:
            #print(traceback.format_exc())
            pass


def setup(bot):
    bot.add_cog(GiveawayCog(bot))
    print("Giveaway is loaded")
