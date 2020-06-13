import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json
import os

class TickitsCog(commands.Cog, name="Tickits"):
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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            db = sqlite3.connect("main.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'tickets.activation_channel'")
            result = cursor.fetchone()
            if result is None:
                return
            if str(after.channel.id) == result[0]:
                await member.move_to(None)
                cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'tickets.category'")
                result = cursor.fetchone()
                category = member.guild.get_channel(int(result[0]))
                exsists = False

                for channel in category.text_channels:
                    if channel.name == f"ticket-{member.id}":
                        exsists = True
                        break

                if exsists:
                    await member.send("You alredy have a ticket running.")
                    return

                channel = await member.guild.create_text_channel(name=f"ticket-{member.id}", category=category)
                await channel.set_permissions(member, read_messages=True)

                embed = discord.Embed(color=self.color, title=f"New ticket")
                embed.add_field(name="User", value=member.mention)
                embed.add_field(name="Time", value=datetime.datetime.now().strftime('%x %X'))
                embed.set_footer(text=f"ID: {member.id}")

                await channel.send("||@here||", embed=embed)

    @commands.command()
    async def close(self, ctx):

        db = sqlite3.connect("main.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'tickets.category'")
        result = cursor.fetchone()
        category = ctx.guild.get_channel(int(result[0]))

        if ctx.channel.category != category:
            return

        with open(f"{ctx.channel.name}.txt", "w") as file:
            history = await ctx.channel.history().flatten()
            out = f"Ticket started at {datetime.datetime.now().strftime('%x %X')}\n\n"
            for message in history[::-1]:
                out += f"{message.created_at.strftime('%x %X')} | {message.author}:  {message.content}\n"
            file.write(out)

        cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'tickets.log'")
        result = cursor.fetchone()
        channel = ctx.guild.get_channel(int(result[0]))

        ticketAuthorID = str(ctx.channel.name)[7:]
        ticketAuthor = ctx.guild.get_member(int(ticketAuthorID))

        time = history[0].created_at - history[-1].created_at

        embed = discord.Embed(color=self.color, title="Ticket closed")
        embed.add_field(name="Closed by:", value=f"{ctx.author.mention}\n({ctx.author.id})")
        embed.add_field(name="Ticket requested by:", value=f"{ticketAuthor.mention}\n({ticketAuthor.id})")
        embed.add_field(name="‎", value="‎‎")
        embed.add_field(name="Ticket created at:", value=history[-1].created_at.strftime('%x %X'))
        embed.add_field(name="Ticket duration:", value=str(time))
        embed.add_field(name="‎", value="‎‎")
        embed.set_footer(text="Download full ticket log below.")

        await channel.send(embed=embed)
        await channel.send(file=discord.File(f"{ctx.channel.name}.txt"))
        os.remove(f"{ctx.channel.name}.txt")

        await ctx.channel.delete()

def setup(bot):
    bot.add_cog(TickitsCog(bot))
    print("Tickits is loaded")
