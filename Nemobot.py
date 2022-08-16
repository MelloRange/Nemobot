import discord
from discord.ext import commands
import json
import os
import sys

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = config["prefix"], intents=intents)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name = f'{config["prefix"]}help'))


if __name__ == "__main__":
    for file in os.listdir(f"./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


bot.run(config["token"])