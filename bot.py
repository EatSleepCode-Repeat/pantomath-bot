import discord
import datetime
from discord.ext import tasks, commands
import asyncio
import sys
import traceback

bot = commands.Bot(command_prefix = ';;', case_insensitive=True )
bot.remove_command("help")

@bot.event
async def on_ready():
    x = datetime.datetime.now()
    print(str(x) + ' ' + 'Logged in as', bot.user)
    print("\n")

initial_extensions = [
                      "cogs.moderation",
                      "cogs.poll",
                      "cogs.giveAwey",
                      "cogs.tickits",
                      "cogs.stats",
                      "cogs.cnjokes",
                     ]

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"failed to load extension {extension}", file=sys.stderr)
            traceback.print_exc(e)


bot.run("NzIwMzY5MDc2MDA2MDI3Mjg0.XuE-BA.MS9jd9L5kjb0bWxkBZzdssHEJb4")
