import os
import sqlite3
import discord
import asyncio
from discord.ext import commands

from ..db import db

class Messagelog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot


	@commands.command()
	async def codeword(self, ctx, codeword=None):
		async def runsequence():
			#If correct codeword, prompts users to type where they received invite link.
			embed=discord.Embed(title="{}, please specify where exactly you got the invite link".format(ctx.message.author.display_name),
								description="**e.g.: weblink/URL or a friend's discord name.**\nType your answer in the chat. This message will expire in 5 minutes.",
								color=discord.Color.teal())
			botmessage = await ctx.send(embed=embed)
			author = ctx.message.author

			def check(m):
				return m.author == author

			try:
				#If response is one of the generic responses, it will prompt to redo input until correct.
				while True:
					response = await self.bot.wait_for('message', check=check, timeout=60*5)
					if response.content.lower() in ['youtube', 'video', 'youtube video', 'video url'] or 'discord.gg' in response.content:
						embed = discord.Embed(
							title="Please be more specific.\n**e.g.: weblink/URL or a friend's discord name.**",
							description='Type your answer in the chat. This message will expire in 5 minutes.',
							color=discord.Color.red())
						await ctx.send(embed=embed)
					else:
						break
				
				embed=discord.Embed(title="{}, your message has been sent to the moderators.".format(ctx.message.author.display_name), description='Please be patient while they review it.\nIf you do not get a response in 1-2 days, please re-do the command or contact a moderator.', color=0x2ecc71)

				#Gets server defined waiting-log channel id.
				channel = self.bot.get_channel(db.get_one('SELECT waiting_log FROM Servers WHERE server_id=?', ctx.message.guild.id))

				#Deletes all of a user's messages in the waiting room.
				async for message in self.bot.get_channel(db.get_one('SELECT waiting_room FROM Servers WHERE server_id=?', ctx.message.guild.id)).history(limit=200):
					if message.author == ctx.message.author and not message.pinned:
						await message.delete()


				#Checks for warnings on the user across all servers.
				warnings = db.get_one('SELECT * FROM Warns WHERE user_id=?', ctx.message.author.id)
				if warnings == None:
					warnings = 'None'
				else:
					warnings = "❗ Existing warnings, please check this user's warning history."

				#Sends message to appropriate channel.
				modmail = await channel.send(f"""#waiting-room message
												> **User:** {ctx.message.author.mention}
												> **Link from:** {response.content}
												> **Previous warnings?:** {warnings}
												""")
				await modmail.add_reaction('✅')
				await modmail.add_reaction('🔁')
				await modmail.add_reaction('🚫')

				return await botmessage.edit(embed=embed)


			except asyncio.TimeoutError:
				embed=discord.Embed(title="{}, Timed out.".format(ctx.message.author.display_name), description='Please re-do the command.', color=discord.Color.red())
				return await botmessage.edit(embed=embed)

		if codeword == None:
			return await ctx.send("Format: >codeword `insert codeword here`\nIf you do not understand how to use this command, please @ the moderators with your codeword and where you got the server link instead.")
		await ctx.message.delete()

		#if codeword matches server defined codeword, proceed
		servercode = db.get_one('SELECT codeword FROM Servers WHERE server_id=?', ctx.message.guild.id)
		if codeword.lower() == servercode[0]:
			await runsequence()
		else:
			embed=discord.Embed(
				title="{}, Codeword Incorrect.".format(ctx.message.author.display_name),
				description='Format: >codeword `insert codeword here` \nPlease read the rules again.',
				color=discord.Color.red())
			return await ctx.send(embed=embed)


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction):

		if reaction.user_id == self.bot.user.id:
			return

		if reaction.channel_id == db.get_one('SELECT waiting_log FROM Servers WHERE server_id=?', ctx.message.guild.id):
			channel = self.bot.get_channel(db.get_one('SELECT waiting_log FROM Servers WHERE server_id=?', ctx.message.guild.id))
			message = await channel.fetch_message(reaction.message_id)

			emoji_list = []
			for react in message.reactions:
				emoji_list.append(react.emoji)

			if '🆗' in emoji_list:
				return
			if reaction.emoji.name not in ['✅', '🚫', '🔁']:
				return
			
			if message.mentions or message.author.id != self.bot.user.id:
				user = message.mentions[0]
				if reaction.emoji.name == '✅':
					role = discord.utils.get(channel.guild.roles, id=db.get_one('SELECT member_role FROM Servers WHERE server_id=?', reaction.guild_id))
					if user not in role.members:
						#Loops to ensure member gets role
						while True:
							await user.add_roles(role)
							if user in role.members:
								break
					await user.send("You have been accepted into Yon and Mello's server!")

				elif reaction.emoji.name == '🚫':
					await user.send("You have been denied entry and banned. Please DM YonKaGor or MelloRange if you believe this is a mistake.")
					await user.ban(reason='Ban on entry')
					db.execute('INSERT INTO Warns(server_id, user_id, description) VALUES(?,?,?)', (reaction.guild_id, user.id, 'Banned in waiting room.',))
					
				elif reaction.emoji.name == '🔁':
					await user.send("You are being asked to re-do the codeword command with a more specific answer. (e.g. website link where you got the server invite)")

				await message.add_reaction('🆗')
		'''
		elif str(reaction.channel_id) in data.load[guild]['channels']['art']:
			data.load[guild]['members'][str(reaction.user_id)]['karma'] += 1
			data.save()
		else:
			return
		'''


def setup(bot):
	bot.add_cog(Messagelog(bot))