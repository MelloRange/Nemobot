import discord
from discord.ext import commands
from discord.ext import tasks
import threading
import os
import json
import sys

import settings

from globals import *

intents = discord.Intents.none()
intents.bans = True
intents.emojis = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.presences = True
intents.reactions = True
intents.typing = True

bot = commands.Bot(command_prefix = ">", intents=intents)
bot.remove_command('help')

if __name__ == "__main__":
	for extension in settings.startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))

@bot.event
async def on_ready():
	print("Bwekhbot is online!")
	await bot.change_presence(activity=discord.Game(name = ">help"))

@bot.event
async def on_guild_join(guild):
	await init_guild_data(data.load, str(guild.id))
	for member in guild.members:
		await init_member_data(str(guild.id), data.load, str(member.id))

	data.save()



@bot.event
async def on_member_join(member):
	await init_member_data(str(member.guild.id), data.load, str(member.id))
	data.load[str(member.guild.id)]['members'][str(member.id)]['is_in_server'] = True
	data.save()

async def init_guild_data(data, guild):
	if not guild in data:
		data[guild] = {}
		data[guild]['password'] = "orange"
		data[guild]['members'] = {}
		data[guild]['channels'] = {}
		data[guild]['channels']['botbanned'] = []
		data[guild]['channels']['expbanned'] = []
		data[guild]['channels']['art'] = []
		data[guild]['channels']['waiting_room'] = "0"
		data[guild]['channels']['waiting_log'] = "0"
		data[guild]['channels']['warning_log'] = "0"
		data[guild]['roles'] = {}
		data[guild]['world'] = {}

async def init_member_data(guild, data, member): 
	if not member in data[guild]['members']:
		data[guild]['members'][member] = {}
		data[guild]['members'][member]['is_in_server'] = True
		data[guild]['members'][member]['warnings'] = 0
		data[guild]['members'][member]['warning_history'] = {}
		data[guild]['members'][member]['warning_history']['number'] = 0
		data[guild]['members'][member]['bans'] = {}
		data[guild]['members'][member]['permissions'] = {}
		data[guild]['members'][member]['weekly_points'] = 0
		data[guild]['members'][member]['level'] = 1
		data[guild]['members'][member]['experience'] = 0
		data[guild]['members'][member]['money'] = {}
		data[guild]['members'][member]['money']['gold'] = 0
		data[guild]['members'][member]['money']['silver'] = 100
		data[guild]['members'][member]['karma'] = 20
		data[guild]['members'][member]['profile'] = {}
		data[guild]['members'][member]['profile']['description'] = "_Type `>profile description` to change your description!_"
		data[guild]['members'][member]['profile']['color'] = 0x474747
		data[guild]['members'][member]['profile']['reference'] = {}
		data[guild]['members'][member]['inventory'] = {}
		data[guild]['members'][member]['inventory']['fish'] = {}
		data[guild]['members'][member]['inventory']['chests'] = {}
		data[guild]['members'][member]['inventory']['dishes'] = {}
		data[guild]['members'][member]['inventory']['ingredients'] = {}
		data[guild]['members'][member]['fish_location'] = "river"
		data[guild]['members'][member]['fish_log'] = {}
		data[guild]['members'][member]['aquarium'] = {}
		data[guild]['members'][member]['aquarium']['1'] = {}
		data[guild]['members'][member]['aquarium']['1']["decor"] = "sand"
		data[guild]['members'][member]['aquarium']['1']["fish"] = []
		data[guild]['members'][member]['aquarium']['1']["slots"] = 2
		data[guild]['members'][member]['recipe_log'] = {}
		data[guild]['members'][member]['cooking'] = {}
		data[guild]['members'][member]['eaten'] = {}
		data[guild]['members'][member]['cooking']["pot"] = []
		data[guild]['members'][member]['fish_upgrades'] = []
		data[guild]['members'][member]['daily'] = False

@bot.event
async def on_message(message):

	channel = str(message.channel.id)
	channels = data.load[str(message.guild.id)]['channels']

	if message.author.bot:
		return

	#if bot is banned in channel, it does not process commands.
	if channel in channels['botbanned']:
		return
	elif (message.content.startswith('>')):
		await bot.process_commands(message)


	if channel in channels['art']:
		await calculate_karma(message.guild, data, message)

	#calculates experience gain.
	if channel in channels['expbanned']:
		return
	elif message_timeout.check(message.author.id):
		await add_experience(message.guild, message.author, 2)
		message_timeout.update(message.author.id)

	await level_up(message.guild, message.author)
	data.save()

async def add_experience(guild, member, exp):
	user = User(guild, member)

	user.data['experience'] += exp
	user.data['weekly_points'] +=1

	#every 5 times add_experience is called, give the user 1 silver.
	if user.exp % 5 == 0:
		user.data['money']['silver'] += 1
	data.save()


async def level_up(guild, member):
	user = User(guild, member)

	experience = user.data['experience']
	lvl_start = user.data['level']
	lvl_end = int(experience ** (1/4))
	if lvl_start < lvl_end:
		user.data['level'] = lvl_end

async def calculate_karma(guild, data, message):
	user = User(guild, message.author)
	guild = Guild(guild)

	if message.attachments or match_url(message.content):
		if message.reference:
			channel = message.guild.get_channel(message.reference.channel_id)
			msg = await channel.fetch_message(message.reference.message_id)
			if msg.author == message.author:
				user.data['karma'] -= 20
			else:
				user.data['karma'] += 10
		else:
			user.data['karma'] -= 20
	elif message.reference:
		channel = message.guild.get_channel(message.reference.channel_id)
		msg = await channel.fetch_message(message.reference.message_id)
		if msg.author != message.author:
			user.data['karma'] += 10

		

	if user.data['karma'] <= 0:
		await message.author.add_roles(message.guild.get_role(int(guild.roles['low_karma'])))
		await message.channel.send(f"{message.author.mention}, you have low karma. Reply to other people's art with the reply function!")
	elif user.data['karma'] > 0 and message.guild.get_role(int(guild.roles['low_karma'])) in message.author.roles:
		await message.author.remove_roles(message.guild.get_role(int(guild.roles['low_karma'])))


@bot.event
async def on_member_remove(member):
	user = User(member.guild, member)

	user.data['is_in_server'] = False
	user.data['weekly_points'] = 0


@bot.command()
async def bwekh(ctx):
	await ctx.send(f'BWEKH! (°<°) {round(bot.latency * 1000)}ms')

#change to listen event when moving cogs

@bot.command()
async def modmail(ctx, *, message):
	'''Send a message to the moderators!
		`>modmail <insert message>`'''
	guild = Guild(ctx.message.guild)

	channel = bot.get_channel(int(guild.channels['modmail']))
	if message is not None:
		await channel.send(f'From {ctx.message.author.mention}: "{message}"')
		await ctx.message.delete()
		return await ctx.send("Your message has been sent successfully.")

	return await ctx.send("Format: >modmail `insert message` \nPlease try again.")

@bot.command()
async def daily(ctx):
	'''Walk nemo for daily money!'''
	guild = Guild(ctx.message.guild)
	user = User(ctx.message.guild, ctx.message.author)
	if user.data["daily"] == False:
		user.data["daily"] = True
		user.data["money"]["silver"] += 40
		return await ctx.send("You walked nemo! <:nemohappy:853219337569566781> +40 silver")
	else:
		return await ctx.send("You already walked nemo today. <:nemosmile:853204511987859476>")

	

@bot.command()
async def help(ctx, more: str = None):
	'''It's this command'''
	
	def format_command(cmd, brief):
		text = cmd.help
		if text == None:
			text = "No description"
		if brief:
			text = text.split('\n')[0]
		return "**{}**: *{}*".format(cmd.name, text)

	if more == None:
		embed = discord.Embed(
			description = "These are the available commands! Type '>help `command name`' for more info!",
			color = 0x2FB7EA
		)
		embed.set_author(name="Help", icon_url=bot.user.avatar_url)
		
		for cog_name in bot.cogs:
			if cog_name in ["Moderator", "Loops", "Admin"]:
				continue

			commands = []
			already_shown = []
			for cmd in bot.walk_commands():
				if cmd.name in already_shown:
					continue
				if cmd.parent != None:
					continue
				if cmd.cog_name == cog_name:
					commands.append(format_command(cmd, True))
					already_shown.append(cmd.name)

			embed.add_field(
				name = cog_name,
				value = '\n'.join(commands),
				inline = False
			)

		commands = []
		already_shown = []
		for cmd in bot.walk_commands():
			if cmd.name in already_shown:
				continue
			if cmd.cog_name == None:
				commands.append(format_command(cmd, True))
				already_shown.append(cmd.name)

		embed.add_field(
			name = "Uncategorized",
			value = '\n'.join(commands),
			inline = False
		)

		return await ctx.send(embed=embed)

	else:
		for cmd in bot.walk_commands():
			if cmd.name == more:
				help_text = cmd.help
				if help_text == None:
					help_text = "No Description"
				embed = discord.Embed(
					description = help_text,
					color = 0x2FB7EA
				)
				embed.set_author(name=cmd.name, icon_url=bot.user.avatar_url)
				return await ctx.send(embed=embed)

		return await ctx.send("Not an available command.")


bot.run(settings.BOT_TOKEN)