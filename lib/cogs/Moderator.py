import os
import discord
import asyncio
import datetime
from discord.ext import commands

from ..db import db

class Moderator(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def warn(self, ctx, member:discord.Member = None, userid = None, *, reason = None):
		if member == None and userid == None:
			return await ctx.send("Format: >warn `insert @ or user ID`")

		if member == None:
			user_id = db.get_one('SELECT user_id FROM Users WHERE user_id=?', userid)
			if user_id == None:
				return await ctx.send("User not found.\nFormat: >warn `insert @ or user ID`")
			member = ctx.message.guild.get_member(user_id)
		else:
			if userid != None:
				if reason == None:
					reason = str(userid)
				else:
					reason = str(userid) + " " + reason


		embed=discord.Embed(title="Issuing warning...", description="", color=0xFFA500)
		embed.set_author(name=f"Warning for @/{member.display_name} ({member.name})")
		msg = await ctx.send(embed=embed)

		time = str(datetime.date.today())
		while(True):
			if reason == None:
				embed=discord.Embed(title="Please enter a reason for the warning.", description="‎", color=0xff0000)
				embed.set_author(name=f"Warning for @/{member.display_name} ({member.name})")
				await msg.edit(embed=embed)

				def check(m):
					return m.author == ctx.message.author

				reason = await self.bot.wait_for('message', check=check)
				reason = reason.content

			warn_log = f"""Warning given to @/{member.display_name} | `{member.name}#{member.discriminator}` | `{member.id}`
Reason cited: **{reason}**
This member now has **{str(int(db.get_one('SELECT COUNT(*) FROM Warns WHERE user_id=?', member.id)) + 1)}** total warnings.
`Given by {ctx.message.author.name} on {time}.`"""
			embed=discord.Embed(title="The following will be sent to the #warning-log. Please check if it is correct.\nReact ✅ to continue, 🔁 to retype the warning, or ❌ to cancel.",
								 description=warn_log, color=0xFFA500)
			embed.set_author(name=f"Warning for {member.name}")
			await msg.edit(embed=embed)

			await msg.add_reaction('✅')
			await msg.add_reaction('🔁')
			await msg.add_reaction('❌')

			def check(reaction, user):
				return user == ctx.message.author and str(reaction.emoji) in ['✅', '🔁', '❌']

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				await msg.clear_reactions()
			except asyncio.TimeoutError:
				embed=discord.Embed(title="‎",
								 description="Please try again.", color=0x606060)
				embed.set_author(name=f"Timed Out")
				return await msg.edit(embed=embed)

			if reaction.emoji == '✅':
				warn_log = f"""Warning given to {member.mention} | `{member.name}#{member.discriminator}` | `{member.id}`
Reason cited: **{reason}**
This member now has **{str(int(db.get_one('SELECT COUNT(*) FROM Warns WHERE user_id=?', member.id)) + 1)}** total warnings.
`Given by {ctx.message.author.name} on {time}.`"""
				break
			elif reaction.emoji == '🔁':
				reason = None
				continue
			elif reaction.emoji == '❌':
				embed=discord.Embed(title="Warning cancelled.",
								 description="‎", color=0x606060)
				return await msg.edit(embed=embed)

		while(True):
			if reason == None:
				embed=discord.Embed(title="Please enter the message for the user.", description="‎", color=0xff0000)
				
				await msg.edit(embed=embed)

				def check(m):
					return m.author == ctx.message.author

				reason = await self.bot.wait_for('message', check=check)
				reason = reason.content

			user_dm = f"""You have been warned in YonKaGor's server by a moderator. Reason cited below:
							> {reason}
Please contact the mods with the `>modmail <insert message here>` if you have any questions."""

			embed=discord.Embed(title="The following will be DMed to the user. Please check if it is correct.\nReact ✅ to continue, 🔁 to retype the message, or ❌ to not send a message.",
								 description=user_dm, color=0xFFA500)
			embed.set_author(name=f"Warning for @/{member.display_name} ({member.name})")
			await msg.edit(embed=embed)

			await msg.add_reaction('✅')
			await msg.add_reaction('🔁')
			await msg.add_reaction('❌')

			def check(reaction, user):
				return user == ctx.message.author and str(reaction.emoji) in ['✅', '🔁', '❌']

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				await msg.clear_reactions()
			except asyncio.TimeoutError:
				embed=discord.Embed(title="Please try again.", description="‎", color=0x606060)
				embed.set_author(name=f"Timed Out")
				return await msg.edit(embed=embed)

			if reaction.emoji == '✅':
				await member.send(user_dm)
				break
			elif reaction.emoji == '🔁':
				reason = None
				continue
			elif reaction.emoji == '❌':
				break


		warning_log = self.bot.get_channel(db.get_one('SELECT warning_log FROM Servers WHERE server_id=?', ctx.message.guild.id))

		db.execute('INSERT OR IGNORE INTO Warns(server_id, user_id, description, issuer_name, issuer_id, warn_date) VALUES(?,?,?,?,?,?)', ctx.message.guild.id, member.id, reason, ctx.message.author.name, ctx.message.author.id, time)
		warn_id = db.get_one('SELECT MAX(warn_id) FROM Warns')
		wm = await warning_log.send(warn_log + f"\nid: {warn_id}")
		db.execute('UPDATE Warns SET message_id=? WHERE warn_id=?', wm.id, warn_id)

		embed=discord.Embed(title="Done!", description="‎", color=0x00ff00)
		embed.set_author(name=f"Warning for @/{member.display_name} ({member.name}) Issued")
		await msg.edit(embed=embed)


	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def warnlist(self, ctx, member:discord.Member = None, userid=None):
		if member == None and userid == None:
			return await ctx.send("Please specify a user.\n>warnlist `insert @ or user ID`")

		if member == None:
			user_id = db.get_one('SELECT user_id FROM Users WHERE user_id=?', userid)
			if user_id == None:
				return await ctx.send("User not found.\n>warnlist `insert @ or user ID`")
			member = ctx.message.guild.get_member(user_id)

		embed=discord.Embed(title=f"{member.display_name}'s warnings", color=0xff0000)
		for warning in db.get_all('SELECT * FROM Warns WHERE user_id=?', member.id):
			embed.add_field(name="id: " + str(warning[2]), 
                value= f"Note: {warning[3]}\n`Given by: {warning[5]}`\n `Given on: {warning[6]}`",
                inline=False)
		await ctx.send(embed=embed)


	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def removewarn(self, ctx, warnid=None):
		if warnid == None:
			return await ctx.send("Please enter the **warning id** you wish to remove. You may see the ID in `>warnlist`.\n>removewarn `insert warning id`")

		warning = db.get_line('SELECT * FROM Warns WHERE warn_id=?', warnid)
		if warning == None:
			return await ctx.send("Warning not found.")

		member = self.bot.get_user(warning[1])
		reason = warning[3]
		given_by = self.bot.get_user(warning[5])
		time = warning[6]

		embed=discord.Embed(title="The following warning will be removed. Please check if it is correct.\nReact ✅ to confirm, or ❌ to cancel.",
			description=f"User: {member.mention}\nNote: {reason}\n`Given by: {warning[5]}`\n `Given on: {time}`", color=0xff0000)
		msg = await ctx.send(embed=embed)

		await msg.add_reaction('✅')
		await msg.add_reaction('❌')

		def check(reaction, user):
			return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
			await msg.clear_reactions()
		except asyncio.TimeoutError:
			embed=discord.Embed(title="Please try again.", description="‎", color=0x606060)
			embed.set_author(name=f"Timed Out")
			return await msg.edit(embed=embed)

		if reaction.emoji == '✅':
			channel = self.bot.get_channel(db.get_one('SELECT warning_log FROM Servers WHERE server_id=?', ctx.message.guild.id))
			message = await channel.fetch_message(warning[7])
			if message != None:
				await message.edit(content=f"""Warning given to {member.mention} | `{member.name}#{member.discriminator}` | `{member.id}`
Reason cited: **{reason}**
This member now has **{str(db.get_one('SELECT COUNT(*) FROM Warns WHERE user_id=?', member.id))}** total warnings.
`Given by {given_by.name} on {time}.`
id: {warnid}
> ❗ This warning has been voided by {ctx.message.author.mention} on {datetime.date.today()}.""")

			db.execute('DELETE FROM Warns WHERE warn_id=?', warnid)
			embed=discord.Embed(title="Warning removed.", description="‎", color=0x00ff00)
		elif reaction.emoji == '❌':
			embed=discord.Embed(title="Cancelled.",
						 description="‎", color=0x606060)

		return await msg.edit(embed=embed)



def setup(bot):
	bot.add_cog(Moderator(bot))