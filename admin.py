import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *
from random import choice

class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def invite(self, ctx, member = None):
		member = finduser(ctx, member)
		if member == None:
			return await ctx.send("Could not find user.")
		await ctx.message.channel.category.set_permissions(member, read_messages=True, send_messages=True, connect=True, speak=True)
		await ctx.send("User invited!")

	@commands.group()
	@commands.has_permissions(administrator = True)
	async def channel(self, ctx):
		if ctx.invoked_subcommand is None:
			return await ctx.send(">channel [add, ban, restrict, art] <channel_id> <(add only) channel_type>")


	@channel.command()
	async def add(self, ctx, channel_id=None, channel_type=None):
		guild = Guild(ctx.guild)

		if channel_type==None:
			return await ctx.send("Format: `>channel add <channel.id> <channel.type>`")

		guild.channels[channel_type] = channel_id
		data.save()
		return await ctx.send(f"Channel added as \"{channel_type}\".")

	@channel.command()
	async def restrict(self, ctx, channel_id=None):
		guild = Guild(ctx.guild)
		if channel_id==None:
			return await ctx.send("Format: `>channel restrict <channel.id>`")

		guild.channels['expbanned'].append(channel_id)
		data.save()
		return await ctx.send("Channel exp gain restricted.")

	@channel.command()
	async def art(self, ctx, channel_id=None):
		guild = Guild(ctx.guild)
		if channel_id==None:
			return await ctx.send("Format: `>channel art <channel.id>`")

		guild.channels['art'].append(channel_id)
		data.save()
		return await ctx.send("Channel added as an art channel.")

	@channel.command()
	async def ban(self, ctx, channel_id=None):
		guild = Guild(ctx.guild)
		if channel_id==None:
			return await ctx.send("Format: `>channel ban <channel.id>`")

		guild.channels['botbanned'].append(channel_id)
		data.save()
		return await ctx.send("Channel banned from bot use.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def role(self, ctx, cmd, role_id, role_type = None):
		guild = Guild(ctx.guild)
		if cmd == "add":
			if role_type != None:
				guild.roles[role_type] = role_id
				await ctx.send(f"Role added as \"{role_type}\".")
			else:
				return await ctx.send("Please enter a role type.")
		else:
			return await ctx.send("Invalid format.")
		data.save()

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def list(self, ctx, cmd):
		guild = str(ctx.guild.id)
		if cmd == "channels":
			keylist = 'Channels'
		elif cmd == "roles":
			keylist = 'Roles'
		else:
			return await ctx.send("Invalid command.")
		embed=discord.Embed(title=keylist, color=discord.Color.blue())
		for channel in data.load[guild][keylist.lower()].keys():
			embed.add_field(name=channel, value=data.load[guild][keylist.lower()][channel], inline=False)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(ban_members = True)
	async def announce(self, ctx, *, message:str = None):
		guild = str(ctx.guild.id)
		if 'announcement' in data.load[guild]['channels']:
			channel = self.bot.get_channel(int(data.load[guild]['channels']['announcement']))
			#add exception for nonexisting channel
			await channel.send(message)
		else:
			await ctx.send("No announcment channel set.")

	@commands.command()
	@commands.has_permissions(ban_members = True)
	async def edit(self, ctx, channel_id, message_id, *, message:str = None):
		channel = self.bot.get_channel(int(channel_id))
		edit_message = await channel.fetch_message(int(message_id))
		if edit_message.author.bot:
			await edit_message.edit(content=message)
			#add exception for nonexisting channel
			await ctx.send("Message edited.")
		else:
			await ctx.send("You cannot edit that message.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def set_keyword(self, ctx, keyword):
		guild = Guild(ctx.guild)
		guild.data['keyword'] = keyword
		data.save()
		return await ctx.send(f"Keyword changed to `{keyword}`.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def log_members(self, ctx):
		for member in ctx.guild.members:
			if not str(member.id) in data.load[str(ctx.guild.id)]['members']:
				data.load[str(ctx.guild.id)]['members'][str(member.id)] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['is_in_server'] = True
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['warnings'] = 0
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['warning_history'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['warning_history']['number'] = 0
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['bans'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['permissions'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['profile'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['weekly_points'] = 0
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['level'] = 1
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['experience'] = 0
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['money'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['money']['gold'] = 0
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['money']['silver'] = 100
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['karma'] = 20
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['profile'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['profile']['description'] = "_Type `>profile description` to change your description!_"
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['profile']['color'] = 0x474747
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['profile']['reference'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['inventory'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['inventory']['fish'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['inventory']['chests'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['fish_location'] = "river"
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['fish_log'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['aquarium'] = {}
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['aquarium']['fish'] = []
				data.load[str(ctx.guild.id)]['members'][str(member.id)]['aquarium']['decor'] = "sand"
				data.save()
				await ctx.send("logged 1.")

		
		await ctx.send("logged.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def givefish(self, ctx, member, fishname):
		member = finduser(ctx, member)
		addItem(data.load[str(ctx.guild.id)]['members'][str(member.id)]['inventory']['fish'], fishname, 1)
		return await ctx.send(f'gave {fishname}')



	@commands.command()
	@commands.has_permissions(administrator = True)
	async def update_data(self, ctx):
		for member in data.load[str(ctx.guild.id)]['members']:
			data.load[str(ctx.guild.id)]['members'][member]['daily'] = False

		data.save()
		return await ctx.send("updated data.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def check_version(self, ctx):
		return await ctx.send("Version 1.3.4")

def setup(bot):
	bot.add_cog(Admin(bot))