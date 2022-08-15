import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *

class Loops(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def run_weather(self, ctx):
		global change_weather

		@tasks.loop(hours = 12)
		async def change_weather(self, ctx):
			guild = Guild(ctx.guild)
			guild.world['weather'] = random.choice(list(staticdata.load['weather']))
			data.save()

		change_weather.start(self, ctx)
		await ctx.send("started loop.")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def run_daily(self, ctx):
		global reset_daily

		@tasks.loop(hours = 24)
		async def reset_daily(self, ctx):
			guild = Guild(ctx.guild)
			for member in data.load[str(ctx.guild.id)]['members']:
				if data.load[str(ctx.guild.id)]['members'][member]["daily"] == True:
					data.load[str(ctx.guild.id)]['members'][member]["daily"] = False
			data.save()

		reset_daily.start(self, ctx)
		await ctx.send("reset daily loop.")


	@commands.command()
	@commands.has_permissions(administrator = True)
	async def start_loop(self, ctx):
		global warning_reset
		global leaderboard_reset

		@tasks.loop(hours = 24 * 7)
		async def warning_reset(self, ctx):
			for member in ctx.guild.members:
				user = User(ctx.guild, member)
				user.data['warnings'] = 0

		@tasks.loop(hours = 24 * 7)
		async def leaderboard_reset(self, ctx):
			guild = Guild(ctx.guild)
			#see if possible in O(1)
			for member in ctx.guild.get_role(int(guild.roles["most_active"])).members:
				await member.remove_roles(ctx.guild.get_role(int(guild.roles["most_active"])))
			#add top leaderboard positions
			lead_dict = {}
			for member in ctx.guild.get_role(int(guild.roles["member_role"])).members:
				if not str(member.id) in guild.members:
					continue;

				user = User(ctx.guild, member)
				if user.data['weekly_points'] == 0:
					continue;

				lead_dict[str(member.id)] = user.data['weekly_points']

			top_users = {k: v for k, v in sorted(lead_dict.items(), key=lambda item: item[1], reverse=True)[:10]}
			print(top_users)
			for postion, user in enumerate(top_users):
				await ctx.guild.get_member(int(user)).add_roles(ctx.guild.get_role(int(guild.roles["most_active"])))

			for member in ctx.guild.get_role(int(guild.roles["member_role"])).members:
				print(member)
				if not str(member.id) in guild.members:
					continue;
				user = User(ctx.guild, member)
				user.data['weekly_points'] = 0
		warning_reset.start(self, ctx)
		leaderboard_reset.start(self, ctx)
		data.save()
		await ctx.send("Started loop.")


	@commands.command()
	@commands.has_permissions(administrator = True)
	async def end_loop(self, ctx):
		warning_reset.cancel()
		leaderboard_reset.cancel()
		await ctx.send("Ended loop.")






def setup(bot):
	bot.add_cog(Loops(bot))