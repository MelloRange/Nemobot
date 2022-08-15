import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *

class Fish(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['f'])
	async def fish(self, ctx):
		'''Catch a fish! Enter any message when the ! pops up. Uses 1 bait.
		Aliases: f'''

		class Fishtype:
			def __init__(self, percent):
				self.rarity = self.getRarity(percent)
				self.grammar = self.getGrammar()
				self.percent = percent

			def getRarity(self, percent):
				for rarity in staticdata.load['fish_rarity']:
					if percent <= staticdata.load['fish_rarity'][rarity]['percent']:
						return rarity

			def getGrammar(self):
				return staticdata.load['fish_rarity'][self.rarity]['grammar']
			


		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		if not 'bait' in user.inven:
			return await ctx.send('You have no bait!\n Buy more using `>buy bait <insert amount>`')



		
		randomPause = random.randint(3, 11)
		pause = 2

		curr_weather = staticdata.load["weather"][guild.world["weather"]]["emote"]
		curr_location = staticdata.load["location"][user.data["fish_location"]]["emote"]
		curr_bait = ":worm: " + str(user.inven['bait'])
		curr_dish = ""
		if user.data["eaten"]:
			for dish in user.data["eaten"]:
				curr_dish = f'{staticdata.load["recipes"][dish.lower()]["emote"]} {user.data["eaten"][dish]}'
				break
		message = await ctx.send(f"{curr_weather} {curr_location} {curr_bait} {curr_dish} \n{ctx.message.author.mention} .")
		author = ctx.author

		subtractItem(user.inven, 'bait', 1)
		randomPercent = random.random()
		weather = guild.world['weather']

		eatdish = ""
		if user.data["eaten"]:
			for dish in user.data["eaten"]:
				eatdish = dish
				if dish == "common stew":
					randomPercent = staticdata.load['fish_rarity']["common"]['percent']
				elif dish == "uncommon stew":
					randomPercent = staticdata.load['fish_rarity']["uncommon"]['percent']
				elif dish == "rare stew":
					randomPercent = staticdata.load['fish_rarity']["rare"]['percent']
				elif dish == "ultra rare stew":
					randomPercent = staticdata.load['fish_rarity']["ULTRA rare"]['percent']
				elif dish == "legendary stew":
					randomPercent = staticdata.load['fish_rarity']["LEGENDARY"]['percent']
				elif dish == "sardines in oil" or dish == "shrimp cocktail":
					randomPause = random.randint(2, 5)
				elif dish == "ganjang gejang":
					randomPercent = staticdata.load['fish_rarity']["chest"]['percent']
				elif dish == "lobster tail":
					while(randomPercent <= staticdata.load['fish_rarity']["common"]['percent']):
						randomPercent = random.random()
				elif dish == "onigiri":
					weather = "sunny"
				elif dish == "seaweed salad":
					weather = "cloudy"
				elif dish == "seaweed soup":
					weather = "rainy"

			subtractItem(user.data["eaten"], eatdish, 1)

		fishtype = Fishtype(randomPercent)

		while pause < randomPause :
			await asyncio.sleep(0.5)
			await message.edit(content= curr_weather + ' ' + curr_location + ' '  +curr_bait + ' '  +curr_dish +'\n' + ctx.message.author.mention + ' ' + '. ' * pause)
			pause += 1

		await asyncio.sleep(0.5)
		await message.edit(content=curr_weather + ' ' + curr_location + ' ' +curr_bait + ' '  +curr_dish +'\n' + ctx.message.author.mention + ' ' + '. ' * pause + '!')


		startCatch = time.time()

		try:
			await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=2)

		except asyncio.TimeoutError:
			return await ctx.send('Too late! The fish escaped...')

		message = ""

		if (ctx.message.author == author):
			endCatch = time.time()
			timeElapsed = endCatch - startCatch
			if timeElapsed < 2:

				if fishtype.rarity == "chest":
					currentchest = []
					for chest in staticdata.load["chests"]:
						if weather in staticdata.load["chests"][chest]['weather']:
							if user.data['fish_location'] in staticdata.load["chests"][chest]['location']:
								currentchest.append(chest)

					chestObtained = random.choice(currentchest)
					addItem(user.inven['chests'], chestObtained, 1)
					return await ctx.send(f'{ctx.message.author.mention}, you fished up a {chestObtained}!')

				currentfish = []
				for fish in staticdata.load["fish"]:
					if weather in staticdata.load["fish"][fish]['weather']:
						if user.data['fish_location'] in staticdata.load["fish"][fish]['location']:
							if fishtype.rarity == staticdata.load["fish"][fish]['rarity']:
								currentfish.append(fish)


				fishObtained = random.choice(currentfish)

				if not fishObtained in user.data['fish_log']:
					user.data['fish_log'].update({fishObtained : {
						"total_caught": 1, 
						"first_obtained": str(date.today())
						}})
					isNew = True
				else:
					user.data['fish_log'][fishObtained]["total_caught"] += 1
					isNew = False

				new = ""
				if isNew:
					new ="<:newsymbol:924647546914209834>"


				addItem(user.inven['fish'], fishObtained, 1)
				message = f"{ctx.message.author.mention}, you caught {fishtype.grammar} {staticdata.load['fish_rarity'][fishtype.rarity]['emote']} {fishtype.rarity} {new} {staticdata.load['fish'][fishObtained]['emote']} {fishObtained}!\n_{staticdata.load['fish'][fishObtained]['description']}_"

			else:
				message = 'Too late! The fish escaped...'

			data.save()
			return await ctx.send(f'{message}')
			

	@commands.command(aliases = ['loc'])
	async def location(self, ctx, location = None):
		'''Change your fishing location.'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)
		if location is None:
			return await ctx.send("Please type in a location: River, Lake, Ocean Reef\n`>location <insert location>`")

		if location.lower() in staticdata.load["location"]:
			if location.lower() == "reef":
				if not "boat" in user.data["fish_upgrades"]:
					return await ctx.send("You need a boat to fish in the reef.\nCheck >shop")


			user.data['fish_location'] = location.lower()
			return await ctx.send(f"Changed your location to: {location.capitalize()}")

		return await ctx.send(f"Location does not exist.")


	@commands.command()
	async def fishbook(self, ctx):
		'''Checks the fish you caught.'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		totalfish = 0
		caughtfish = 0
		for fish in staticdata.load['fish']:
			totalfish += 1
			if fish in user.data["fish_log"]:
				caughtfish +=1

		completion = "\u200b"
		if caughtfish == totalfish:
			completion = "👑"

		title = f"{completion} {ctx.message.author.display_name}'s fishbook"
		description = f"{caughtfish}/{totalfish} discovered"
		color = user.profile['color']


		numpages = 6

		page1 = discord.Embed (
			title = f"{title} 1/{numpages}",
			description = description,
			colour = color
		)

		page2 = discord.Embed (
			title = f"{title} 2/{numpages}",
			description = description,
			colour = color
		)
		page3 = discord.Embed (
			title = f"{title} 3/{numpages}",
			description = description,
			colour = color
		)
		page4 = discord.Embed (
			title = f"{title} 4/{numpages}",
			description = description,
			colour = color
		)
		page5 = discord.Embed (
			title = f"{title} 5/{numpages}",
			description = description,
			colour = color
		)
		page6 = discord.Embed (
			title = f"{title} 6/{numpages}",
			description = description,
			colour = color
		)
		pages = [page1, page2, page3, page4, page5, page6]

		
		fishies = -1
		pagenum = -1
		for fish in staticdata.load['fish']:
			fishies +=1
			if fishies % 21 == 0:
				pagenum +=1
			if fish in user.data["fish_log"]:
				weatherlog = "- "
				locationlog = "- "
				for weather in staticdata.load["fish"][fish]["weather"]:
					weatherlog += f'{weather.capitalize()} - '
				for location in staticdata.load["fish"][fish]["location"]:
					locationlog += f'{location.capitalize()} - '

				pages[pagenum].add_field(
					name=f'{staticdata.load["fish_rarity"][staticdata.load["fish"][fish]["rarity"]]["emote"]} {staticdata.load["fish"][fish]["emote"]} {fish.capitalize()}', 
					value=f'Total caught: {user.data["fish_log"][fish]["total_caught"]}\n{user.data["fish_log"][fish]["first_obtained"]}\n_{weatherlog}_\n_{locationlog}_', 
					inline=True
					)
			else:
				pages[pagenum].add_field(name="❔ Undiscovered", value=f"???", inline=True)

		message = await ctx.send(embed = page1)

		await message.add_reaction('⏮')
		await message.add_reaction('◀')
		await message.add_reaction('▶')
		await message.add_reaction('⏭')

		def check(reaction, user):
			return user == ctx.author

		i = 0
		reaction = None

		while True:
			if str(reaction) == '⏮':
				i = 0
				await message.edit(embed = pages[i])
			elif str(reaction) == '◀':
				if i > 0:
					i -= 1
					await message.edit(embed = pages[i])
			elif str(reaction) == '▶':
				if i < numpages-1:
					i += 1
					await message.edit(embed = pages[i])
			elif str(reaction) == '⏭':
				i = numpages-1
				await message.edit(embed=pages[i])
			
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
				await message.remove_reaction(reaction, user)
			except:
				break

		await message.clear_reactions()



def setup(bot):
	bot.add_cog(Fish(bot))