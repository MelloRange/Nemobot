import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *

class Garden(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['g'])
	async def garden(self, ctx):
		'''Check your or another user's garden.
		Aliases: g'''
		if ctx.invoked_subcommand is None:
			if ctx.subcommand_passed is None:
				user = User(ctx.guild, ctx.message.author)
				userobject = ctx.message.author
			else:
				member = finduser(ctx, ctx.subcommand_passed)
				if member is None:
					return await ctx.send("Could not find user.")
				user = User(ctx.guild, member)
				userobject = member

			embed=discord.Embed(title=f"{ctx.message.author.display_name}'s Garden", color=int(user.profile["color"]))
			for plot in user.data["garden"]:
				flower = user.data["garden"][plot]["flower"]
				growth = user.data["garden"][plot]["growth"]
				cost = user.data["garden"][plot]["cost"]
				day_planted = user.data["garden"][plot]["day_planted"]
				emote = getEmote(flower, growth)

				days_old = (day_planted - date.today()).days()

			def getEmote(flower, growth):
				if growth in staticdata.load["flowers"]:
					return staticdata.load["flowers"][growth]["emote"]
				else:
					return staticdata.load["flowers"][flower]


				embed.add_field(name=f'{flower} {emote}', value=f'{}', inline=True)
			embed.add_field(name="\u200b", value="\u200b" + getMessage(user.data["aquarium"]["fish"][:len(user.data["aquarium"]["fish"])//2]), inline=False)
			embed.add_field(name="\u200b", value="\u200b" + getMessage(user.data["aquarium"]["fish"][len(user.data["aquarium"]["fish"])//2:]), inline=True)
			embed.add_field(name="\u200b", value="\u200b" + ground*1 + decor3*1 + decor2*1 + decor1*4 + ground*6 + decor2*1 + decor1*3 + decor3*1 + ground*1 +  decor2*1 + decor1*2 + ground*1, inline=False)



def setup(bot):
	bot.add_cog(Garden(bot))