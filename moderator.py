import discord
import json
from discord.ext import commands
from globals import *
from random import choice

class Moderator(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction):
		guild = str(reaction.guild_id)
		if reaction.user_id == self.bot.user.id:
			return
		if reaction.channel_id == int(data.load[guild]['channels']['waiting_log']):
			if reaction.emoji.name != '✅' and reaction.emoji.name != '🚫' and reaction.emoji.name != '🔁':
				return
			channel = self.bot.get_channel(int(data.load[guild]['channels']['waiting_log']))
			message = await channel.fetch_message(reaction.message_id)
			if message.mentions or message.author.id != self.bot.user.id:
				user = message.mentions[0]
				if reaction.emoji.name == '✅':
					role = discord.utils.get(channel.guild.roles, id=int(data.load[guild]['roles']['member_role']))
					if user not in role.members:
						while True:
							await user.add_roles(role)
							if user in role.members:
								break
					#if user not in role.members:0-*
					#	await user.add_roles(role)
					#	await user.send("You have been accepted into Yon and Mello's server!")
					await user.send("You have been accepted into Yon and Mello's server!")
				elif reaction.emoji.name == '🚫':
					await user.send("You have been denied entry. Please DM YonKaGor or MelloRange if you believe this is a mistake.")
				elif reaction.emoji.name == '🔁':
					await user.send("You are being asked to re-do the keyword command with a more specific answer. (e.g. website link where you got the server invite)")

				await message.add_reaction('🆗')
		elif str(reaction.channel_id) in data.load[guild]['channels']['art']:
			data.load[guild]['members'][str(reaction.user_id)]['karma'] += 1
			data.save()
		else:
			return

	@commands.command()
	async def keyword(self, ctx, keyword=None):
		async def runsequence():
			embed=discord.Embed(title="{}, please specify where exactly you got the invite link".format(ctx.message.author.display_name),
                                description="**i.e.: video link/url or a friend's discord name.**\nType your answer in the chat. This message will expire in 5 minutes.",
                                color=discord.Color.teal())
			botmessage = await ctx.send(embed=embed)
			author = ctx.message.author

			def check(m):
				return m.author == author

			try:
				while True:
					response = await self.bot.wait_for('message', check=check, timeout=60*5)
					if response.content.lower() in ['youtube', 'video', 'youtube video', 'video url'] or 'discord.gg' in response.content:
						embed = discord.Embed(
                        	title="Please be more specific.",
                        	description='Type your answer in the chat. This message will expire in 5 minutes.',
                        	color=discord.Color.red())
						await ctx.send(embed=embed)
					else:
						break
				
				embed=discord.Embed(title="{}, your message has been sent to the moderators.".format(ctx.message.author.display_name), description='Please be patient while they review it.', color=0x2ecc71)
				channel = self.bot.get_channel(int(data.load[guild]['channels']['waiting_log']))
				async for message in self.bot.get_channel(int(data.load[guild]['channels']['waiting_room'])).history(limit=200):
					if message.author == ctx.message.author and not message.pinned:
						await message.delete()
				modmail = await channel.send("#waiting-room message\n> **User:** {}\n> **Keyword:** {}\n> **Link from:** {}".format(ctx.message.author.mention, keyword, response.content))
				await modmail.add_reaction('✅')
				await modmail.add_reaction('🔁')
				await modmail.add_reaction('🚫')
				return await botmessage.edit(embed=embed)
			except asyncio.TimeoutError:
				embed=discord.Embed(title="{}, Timed out.".format(ctx.message.author.display_name), description='Please re-do the command.', color=discord.Color.red())
				return await botmessage.edit(embed=embed)

		if keyword == None:
			return await ctx.send("Format: >keyword `insert keyword`\nIf you do not understand how to use this command, please @ the moderators with your keyword and where you got the server link instead.")
		await ctx.message.delete()

		guild = str(ctx.guild.id)
		if keyword.lower() == data.load[guild]['keyword']:
			await runsequence()
		else:
			embed=discord.Embed(
            	title="{}, Keyword Incorrect.".format(ctx.message.author.display_name),
            	description='Format: >keyword [keyword] \nPlease read the rules again.',
            	color=discord.Color.red())
			return await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def warn(self, ctx, member:discord.Member = None, num:str = None, *, message = None):
		if member == None or num == None:
			return await ctx.send("Format: >warn [@user] [rule #] [(opt.) reason]\nIf warning is for an unspecified rule, please put 0 as the rule #.")

		user = User(ctx.guild, member)
		guild = Guild(ctx.guild)

		channel = self.bot.get_channel(int(guild.channels['warning_log']))
		time = str(date.today())

		if message == None:
			if num in staticdata.load['rules']:
				message = staticdata.load['rules'][num]
			else:
				message = "None";

		user.data['warnings'] += 1
		user.data['warning_history']['number'] += 1
		warnNum = str(user.data['warning_history']['number'])
		user.data['warning_history'][warnNum] = {}
		user.data['warning_history'][warnNum]['rule_number'] = num
		user.data['warning_history'][warnNum]['reason'] = message
		user.data['warning_history'][warnNum]['date'] = time
		user.data['warning_history'][warnNum]['given_by'] = ctx.message.author.name

		await ctx.message.delete()
		await ctx.send(f"{member.mention}, you have been given a warning for breaking rule **{num}**.\nReason cited: {message}")
		channel = self.bot.get_channel(int(guild.channels['warning_log']))
		await channel.send(f"Warning given to {member.mention} | `{member.name}#{member.discriminator}` | `{member.id}`\nReason cited: {message}\nThis member now has {len(user.data['warning_history'])-1} total warnings, {user.data['warnings']} warnings this week.\n`Given by {ctx.message.author.name} on {str(date.today())}.`")
		data.save()

		if user.data['warnings'] >= 2:
			member.add_roles(ctx.guild.get_role(int(guild.roles["suspended"])))
			return await ctx.send("You have accumulated 2 or more warnings this week. You have been temporarily suspended, please wait for moderation to look over your warnings.")

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def removewarn(self, ctx, member:discord.Member = None, num: str = None):
		guild = Guild(ctx.guild)
		user = User(ctx.guild, member)
		if member == None or num == None:
			return await ctx.send("Format: >removewarn [@user] [warning #]")
		else:
			user.data['warning_history'].pop(num, None)
			data.save()
			return await ctx.send("Removed warning from user.")
			#remove from log.

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def listwarnings(self, ctx, member = None):
		guild = str(ctx.guild.id)
		if member == None:
			return await ctx.send("Please specify a user.")
		else:
			member = finduser(ctx, member)
			user = User(ctx.guild, member)
			embed=discord.Embed(title="{}'s warnings".format(member.display_name), color=discord.Color.red())
			for warning in user.data['warning_history'].keys():
				embed.add_field(
                    name=warning, 
                    value=user.data['warning_history'][warning],
                    inline=False)
			await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def refdel(self, ctx, member=None):
		if member == None:
			return await ctx.send("Format: `>refdel <@user>`")

		member = finduser(ctx, member)
		if member ==None:
			return await ctx.send("Could not find member.")
		user = User(ctx.guild, member)
		
		user.profile['reference'].clear()
		return await ctx.send("Removed all references from user.")

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def slowmode(self, ctx, seconds: int = None):
		if seconds == None:
			return await ctx.send("Format: >slowmode <insert seconds>")
		await ctx.channel.edit(slowmode_delay=seconds)
		await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

def setup(bot):
	bot.add_cog(Moderator(bot))