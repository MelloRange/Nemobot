import os
import sqlite3
import discord
import asyncio
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..db import db
from ..db import report

class Admin(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="setcode") 
	async def setcode(self, ctx, codeword=None):
		"""
		Changes the code word after it has been set.
		Usage: >setcode [new codeword]
		"""
		if codeword is None:
			return await ctx.send('Format: `>setcode [new code]`.\nPlease re-run the command with the new desired code.')

		db.execute('''UPDATE Servers SET codeword=? WHERE Servers.server_id=?;''', codeword, ctx.guild.id)
		await ctx.send(f'Codeword successfully changed to `{codeword}`')

	@commands.command() 
	async def addmod(self, ctx, member:discord.Member = None, userid = None):

		if member == None and userid == None:
			return await ctx.send("Format: >flag `insert @ or user ID`")

		if member == None:
			user_id = db.get_one('SELECT user_id FROM Users WHERE user_id=?', userid)
			if user_id == None:
				return await ctx.send("User not found.\nFormat: >flag `insert @ or user ID`")
			member = ctx.guild.get_member(user_id)


		db.execute('INSERT OR IGNORE INTO Mods(server_id, user_id, name) VALUES(?,?,?)', ctx.guild.id, member.id, member.name)
		await ctx.send(f'Added {member.mention} to list of mods.')

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction):

		if reaction.user_id == self.bot.user.id:
			return

		if reaction.message_id == db.get_one('SELECT mod_log_msg FROM Servers WHERE server_id=?', reaction.guild_id):
			if reaction.emoji.name == 'Ⓜ️':
				db.execute('UPDATE Mods SET is_on_duty=1 WHERE server_id=? AND user_id=?', reaction.guild_id, reaction.user_id)
				return

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, reaction):
		if reaction.user_id == self.bot.user.id:
			return

		if reaction.message_id == db.get_one('SELECT mod_log_msg FROM Servers WHERE server_id=?', reaction.guild_id):
			if reaction.emoji.name == 'Ⓜ️':
				db.execute('UPDATE Mods SET is_on_duty=0 WHERE server_id=? AND user_id=?', reaction.guild_id, reaction.user_id)
				return

	@commands.command() 
	async def setclock(self, ctx, msg_id=None):
		db.execute('UPDATE Servers SET mod_log_msg=? WHERE server_id=?', int(msg_id), ctx.guild.id)
		print(f'set clock')


	@commands.command() 
	async def getreport(self, ctx):
		await ctx.send(file=discord.File("./data/db/send_report.xlsx"))

'''    @tasks.loop(hours=1.0)
    async def getclock(self):
    	for mod_id in db.get_column('SELECT user_id FROM Mods')'''
    		


def setup(bot):
	bot.add_cog(Admin(bot))