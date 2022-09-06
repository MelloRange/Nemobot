import discord
from discord.ext import commands
import json
import os
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from lib.db import db
from lib.db import report

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
        report.send_report(self.scheduler)
        super().__init__(command_prefix=config["prefix"], intents=intents)

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        await self.scan_message(message)

    # I literally copy and pasted this code from my own bots. Its been field tested and works really well. I'll
    # modify it and other code tomorrow, but I'm pushing this to Git to make sure I can work on this from my
    # other machine later.
    async def scan_message(message):
        """
        The primary anti-scam method. This method is given a message, counts the number of flags in a given message,
        then
        does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+
        flags.
        Last docstring edit: -Autumn V1.14.4
        Last method edit: -Autumn V1.14.5
        :param message: the message sent
        :return: None
        """
        # every word in the blacklist is part of real nitro scams I've encountered in the wild. words are found in a
        # message, the message will get a flag.
        blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)',
                     "who's first? :)"]
        code = 'plsdontban'
        
        flags = 0
        content = message.content.lower()
    
        for word in blacklist:
            index = content.find(word)
            if index != -1:
                flags += 1
        
        # messages with one or no flags get ignored. messages with two or more get flagged and logged for mods to see.
        # two flags makes a note in the log that there's a possible scam. Usually a false alarm and harmless.
        # three or more flags gets deleted and is usually an actual scam.
        if flags < 2:
            return
        else:
            if flags >= 3:
                await message.delete()
        
            content = message.content.replace('@', '@ ')
        
            channel = message.guild.get_channel(log_channel) # TODO: fix this to be a dedicated log channel
        
            embed = discord.Embed(title='Possible Scam in #' + str(message.channel.name), color=0xFF0000)
            embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar_url)
            embed.add_field(name='message', value=content, inline=False)
            embed.add_field(name='Flags', value=str(flags), inline=False)
            embed.add_field(name='Sender ID', value=message.author.id)
            embed.add_field(name='Channel ID', value=message.channel.id)
            embed.add_field(name='Message ID', value=message.id)
        
            if flags < 3:
                # if the message was not deleted, the message URL is included if it is a real scam so the mods can jump
                # to it directly
                embed.add_field(name='URL', value=message.jump_url, inline=False)
            await channel.send(embed=embed)

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