import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *

class Cooking(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def pot(self, ctx):
		'''Check what ingredients you have in your pot.
		Subcommands:
		`>pot add <ingredient name, ingredient name, ingredient name>`
		`>pot remove <ingredient name, ingredient name, ingredient name>`
		`>pot clear`
		'''
		if ctx.invoked_subcommand is None:
			user = User(ctx.guild, ctx.message.author)
			guild = Guild(ctx.guild)
			
			return await ctx.send(f'Ingredients in your pot: `{", ".join(user.data["cooking"]["pot"])}`')

	@pot.command()
	async def add(self, ctx, *, ingredientlist = None):
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)
		if ingredientlist == None:
			return await ctx.send("Please retype the command with the ingredients you want to add.\nMake sure they are commma seperated.\n`>pot add <ingredient1>, <ingredient2>, <ingredient3>`")
		ingredientlist = ingredientlist.split(", ")
		response = []
		for ingredient in ingredientlist:
			if ingredient.lower() in user.inven["fish"]:
				user.data["cooking"]["pot"].append(ingredient.lower())
				subtractItem(user.inven["fish"], ingredient.lower(), 1)
			elif ingredient.lower() in user.inven["ingredients"]:
				user.data["cooking"]["pot"].append(ingredient.lower())
				subtractItem(user.inven["ingredients"], ingredient.lower(), 1)
			else:
				response.append(ingredient.lower())

		if response:
			return await ctx.send(f'Could not find the following ingredients: {", ".join(response)}\nThe rest have been added to your pot.')

		return await ctx.send("Added the ingredients to your pot.")

	@pot.command()
	async def remove(self, ctx, *, ingredientlist = None):
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)
		if ingredientlist == None:
			return await ctx.send("Please retype the command with the ingredients you want to remove.\nMake sure they are commma seperated.\n`>pot remove <ingredient1>, <ingredient2>, <ingredient3>`")
		ingredientlist = ingredientlist.split(", ")
		response = []
		for ingredient in ingredientlist:
			if ingredient.lower() in user.data["cooking"]["pot"]:
				user.data["cooking"]["pot"].remove(ingredient.lower())
				if ingredient in staticdata.load["fish"]:
					addItem(user.inven["fish"], ingredient.lower(), 1)
				elif ingredient in staticdata.load["ingredients"]:
					addItem(user.inven["ingredients"], ingredient.lower(), 1)
			else:
				response.append(ingredient.lower())

		if response:
			return await ctx.send(f'Could not find the following ingredients: {", ".join(response)}\nThe rest have been added to your inventory.')

		return await ctx.send("Removed the ingredients from your pot.")

	@pot.command()
	async def clear(self, ctx):
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)
		for item in user.data["cooking"]["pot"]:
			if item in staticdata.load["fish"]:
				addItem(user.inven["fish"], item.lower(), 1)
			elif ingredient in staticdata.load["ingredients"]:
				addItem(user.inven["ingredients"], ingredient.lower(), 1)
		user.data["cooking"]["pot"].clear()
		data.save()

		return await ctx.send("Cleared your pot.")


	@commands.command()
	async def cook(self, ctx, *, dishname = None):
		'''Cook the ingredients in your pot.
		Subcommands:
		`cook <dishname>`'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		def isSubList(lista, listb):
			listbcopy = listb.copy() 
			for item in lista:
				if item in listbcopy:
					listbcopy.remove(item)
				else:
					return False
			return True

		if dishname == None:
			if not user.data["cooking"]["pot"]:
				return await ctx.send("No ingredients in your pot!")
			checktag = []
			for ingredient in user.data["cooking"]["pot"]:
				if ingredient in staticdata.load["fish"]:
					checktag += staticdata.load["fish"][ingredient]["tags"]
				elif ingredient in staticdata.load["ingredients"]:
					checktag += staticdata.load["ingredients"][ingredient]["tags"]


			recipeCandidates = {}
			for recipe in staticdata.load["recipes"]:
				lista = staticdata.load["recipes"][recipe]["ingredients"]
				listb = checktag
				if isSubList(lista, listb):
					recipeCandidates[recipe] = staticdata.load["recipes"][recipe]["priority"]

			recipeCandidates = {k: v for k, v in sorted(recipeCandidates.items(), key=lambda item: item[1], reverse=True)}
			user.data["cooking"]["pot"].clear()
			if recipeCandidates:
				recipe = list(recipeCandidates.keys())[0]
				addItem(user.inven["dishes"], recipe, 1)
				if not recipe in user.data["recipe_log"]:
					user.data['recipe_log'].update({recipe : {
							"total_cooked": 1, 
							"first_obtained": str(date.today())
							}})
					isNew = True
				else:
					user.data['recipe_log'][recipe]["total_cooked"] +=1
					isNew = False

				new = ""
				if isNew:
					new ="<:newsymbol:924647546914209834>"

				data.save()
				return await ctx.send(f'Congratulations! You cooked a(n): {new}{staticdata.load["recipes"][recipe]["emote"]}{recipe}')
			else:
				addItem(user.inven["ingredients"], "broth", 1)
				return await ctx.send(f"The recipe failed... but you salvaged x1 broth.")

		else:
			if dishname.lower() in user.data["recipe_log"]:
				checktag = []
				for ingredient in staticdata.load["recipes"][dishname.lower()]["ingredients"]:
					remove = ""
					for fish in user.inven["fish"]:
						if ingredient in staticdata.load["fish"][fish]["tags"]:
							remove = fish
							user.data["cooking"]["pot"].append(remove)
							checktag += staticdata.load["fish"][fish]["tags"]
							break
					if not remove == "":
						subtractItem(user.inven["fish"], remove, 1)
						continue
					for ing in user.inven["ingredients"]:
						if ingredient in staticdata.load["ingredients"][ing]["tags"]:
							remove = ing
							user.data["cooking"]["pot"].append(remove)
							checktag += staticdata.load["ingredients"][ing]["tags"]
							break
					if not remove == "":
						subtractItem(user.inven["ingredients"], remove, 1)

				lista = staticdata.load["recipes"][dishname.lower()]["ingredients"]
				listb = checktag
				if isSubList(lista, listb):
					recipe = dishname.lower()

					user.data["cooking"]["pot"].clear()
					addItem(user.inven["dishes"], recipe, 1)

					return await ctx.send(f'Congratulations! You cooked a(n): {staticdata.load["recipes"][recipe]["emote"]}{recipe}')

				else:
					for item in user.data["cooking"]["pot"]:
						if item in staticdata.load["fish"]:
							addItem(user.inven["fish"], item.lower(), 1)
						elif item in staticdata.load["ingredients"]:
							addItem(user.inven["ingredients"], item.lower(), 1)
					user.data["cooking"]["pot"].clear()
					return await ctx.send("You do not have enough ingredients to make that dish.")

			else:
				return await ctx.send("You do not know that dish.")

		


	@commands.command()
	async def eat(self, ctx, *, dish=None):
		'''Eat a dish.
		>eat <insert dishname>'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)
		if not dish.lower() in user.inven["dishes"]:
			return await ctx.send("You don't have that dish.")
		subtractItem(user.inven["dishes"], dish.lower(), 1)
		user.data["eaten"].clear()
		user.data["eaten"][dish.lower()] = staticdata.load["recipes"][dish.lower()]["charges"]
		data.save()
		return await ctx.send(f'You ate a(n) {dish.lower()}!\n{staticdata.load["recipes"][dish.lower()]["description"]}')

	@commands.command()
	async def eaten(self, ctx):
		user = User(ctx.guild, ctx.message.author)
		for dish in user.data["eaten"]:
			return await ctx.send(f'Current dish eaten: {dish}\n{staticdata.load["recipes"][dish.lower()]["description"]}')
		return await ctx.send(f'Current dish eaten: None')


	@commands.command()
	async def cookbook(self, ctx):
		'''Checks your recipes.'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		totalrecipes = 0
		foundrecipes = 0
		for recipe in staticdata.load['recipes']:
			totalrecipes += 1
			if recipe in user.data["recipe_log"]:
				foundrecipes +=1

		completion = "\u200b"
		if foundrecipes == totalrecipes:
			completion = "👑"

		title = f"{completion} {ctx.message.author.display_name}'s cookbook"
		description = f"{foundrecipes}/{totalrecipes} discovered"
		color = user.profile['color']


		numpages = 1

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
			title = title + " 4/5",
			description = description,
			colour = color
		)
		page5 = discord.Embed (
			title = title + " 5/5",
			description = description,
			colour = color
		)

		pages = [page1]

		
		recipes = 0
		pagenum = 0
		for recipe in staticdata.load['recipes']:
			recipes +=1
			if recipes % 20 == 0:
				pagenum +=1
			if recipe in user.data["recipe_log"]:
				ingredientlog = "- "
				for ingredient in staticdata.load["recipes"][recipe]["ingredients"]:
					ingredientlog += f'_{ingredient.capitalize()}_ - '

				pages[pagenum].add_field(
					name=f'{staticdata.load["recipes"][recipe]["emote"]} {recipe.capitalize()}', 
					value=f'{staticdata.load["recipes"][recipe]["description"]}\n{ingredientlog}', 
					inline=True
					)
			else:
				pages[pagenum].add_field(name="❔ Undiscovered", value=f'Hint: {staticdata.load["recipes"][recipe]["hint"]}', inline=True)

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
				if i < len(pages):
					i += 1
					await message.edit(embed = pages[i])
			elif str(reaction) == '⏭':
				i = len(pages)-1
				await message.edit(embed=pages[i])
			
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
				await message.remove_reaction(reaction, user)
			except:
				break

		await message.clear_reactions()



def setup(bot):
	bot.add_cog(Cooking(bot))