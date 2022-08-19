import discord
from discord.ext import commands
import json
import os
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from lib.db import db

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


intents = discord.Intents.default()
intents.members = True

class Bot(commands.Bot):
    def __init__(self):
        self.scheduler = AsyncIOScheduler()


        db.autosave(self.scheduler)
        super().__init__(command_prefix=config["prefix"], intents=intents)


    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        self.scheduler.start()
        print(f"Logged in as {bot.user.name}")
        await bot.change_presence(activity=discord.Game(name = f'{config["prefix"]}help'))

    async def on_member_join(member):
        if db.get_one('SELECT user_id FROM user_in_server WHERE user_id=? AND server_id=?', member.id, member.guild.id) == None:
            db.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', member.id)
            db.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', member.guild.id, member.id)
        else:
            db.execute('UPDATE user_in_server SET is_in_server=1 WHERE user_id=?', member.id)

    async def on_member_leave(member):
        db.execute('UPDATE user_in_server SET is_in_server=0 WHERE user_id=?', member.id)

bot = Bot()

if __name__ == "__main__":
    for file in os.listdir(f"./lib/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"lib.cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")

    bot.run(config["token"])