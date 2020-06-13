import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import sqlite3
from time import sleep
import json

class ModerationsCog(commands.Cog, name="Moderations"):
    def __init__(self, bot):
        self.bot = bot
        self.red = 0xfc0322
        self.yellow = 0xeef21e
        self.green = 0x36d233

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
    async def ban(self , ctx, id:int, *, reason="None set"):
        if "mod.ban" in self.get_perms(ctx.author):
            user = ctx.guild.get_member(id)
            if user is None:
                await ctx.send("Invalid id.")
            else:
                if "mod.ban_bypass" in self.get_perms(user):
                    await ctx.send("Cant ban that user.")
                    return
                await user.ban(reason=f"{reason} | issued by: {ctx.author}")
                await ctx.send(f"Banned {user}")

                db = sqlite3.connect("main.db")
                cursor = db.cursor()
                cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'mod.output'")
                result = cursor.fetchone()

                channel = ctx.guild.get_channel(int(result[0]))

                embed = discord.Embed(title="User ban", color=self.red)

                embed.add_field(name="**User**", value=f"{user}\n({user.id})")
                embed.add_field(name="**Moderator**", value=f"{ctx.author}\n({ctx.author.id})")
                embed.add_field(inline=False, name="**Reason**", value=reason)

                await channel.send(embed=embed)
        else:
            await ctx.send("You do not have the required permissions to run this command.")

    @commands.command()
    async def unban(self , ctx, id:int):
        if "mod.unban" in self.get_perms(ctx.author):
            user = discord.Object(id=id)
            if user is None:
                await ctx.send("Invalid id.")
            else:
                try:
                    await ctx.guild.unban(user)
                except:
                    await ctx.send("User is not banned")
                    return
                await ctx.send(f"Unbanned {user.id}")

                db = sqlite3.connect("main.db")
                cursor = db.cursor()
                cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'mod.output'")
                result = cursor.fetchone()

                channel = ctx.guild.get_channel(int(result[0]))

                embed = discord.Embed(title="User unban", color=self.green)

                embed.add_field(name="**User**", value=f"{user.id}")
                embed.add_field(name="**Moderator**", value=f"{ctx.author}\n({ctx.author.id})")

                await channel.send(embed=embed)
        else:
            await ctx.send("You do not have the required permissions to run this command.")

    @commands.command()
    async def kick(self , ctx, id:int, *, reason="None set"):
        if "mod.kick" in self.get_perms(ctx.author):
            user = ctx.guild.get_member(id)
            if user is None:
                await ctx.send("Invalid id.")
            else:
                if "mod.kick_bypass" in self.get_perms(user):
                    await ctx.send("Cant ban that user.")
                    return
                await user.kick(reason=f"{reason} | issued by: {ctx.author}")
                await ctx.send(f"Kicked {user}")

                db = sqlite3.connect("main.db")
                cursor = db.cursor()
                cursor.execute(f"SELECT channel_id FROM channels WHERE channel_type = 'mod.output'")
                result = cursor.fetchone()

                channel = ctx.guild.get_channel(int(result[0]))

                embed = discord.Embed(title="User kick", color=self.yellow)

                embed.add_field(name="**User**", value=f"{user}\n({user.id})")
                embed.add_field(name="**Moderator**", value=f"{ctx.author}\n({ctx.author.id})")
                embed.add_field(inline=False, name="**Reason**", value=reason)

                await channel.send(embed=embed)

        else:
            await ctx.send("You do not have the required permissions to run this command.")


def setup(bot):
    bot.add_cog(ModerationsCog(bot))
    print("Moderations is loaded")
