import discord
import json
from discord.ext import commands
from globals import *
from time import time


class Shop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def shop(self, ctx, cmd=None):
		'''Opens the Bwekhshop!'''
		title = "__**B W E K H S H O P**__"
		if cmd:
			shoplist = None
			for shop in staticdata.load["shop"]:
				if staticdata.load["shop"][shop]["cmd"] == cmd:
					shoplist = staticdata.load["shop"][shop]
					break;

			if shoplist == None:
				return await ctx.send("Not a valid shop index.\nDo `>shop` to see them all.")

			embed = discord.Embed(title=title, description=shoplist["description"], color=0x2FB7EA)
			for item in shoplist["items"]:
				embed.add_field(name=f'{shoplist["items"][item]["emote"]} {item.capitalize()}', value=f'🔹 {shoplist["items"][item]["cost"]}', inline=True)

			return await ctx.send(embed=embed)
		else:
			embed = discord.Embed(title=title, description="List of all the things money can buy here!", color=0x2FB7EA)
			for shop in staticdata.load["shop"]:
				embed.add_field(name=f'>shop {staticdata.load["shop"][shop]["cmd"]}', value=f'{shop.capitalize()}', inline=True)
			return await ctx.send(embed=embed)

	@commands.command(aliases=['pshop', 'ps'])
	async def pawnshop(self, ctx, cmd=None):
		'''Opens the BwekhPawnshop!.'''
		if cmd == "1":
			embed = discord.Embed(title="__**B W E K H S H O P**__", description="Fish listing and prices. Sell fish with `>sell <amount> <fish name>`", color=0x2FB7EA)
			for rarity in staticdata.load["fish_rarity"]:
				if rarity == "chest":
					continue
				embed.add_field(name=f"{rarity.capitalize()} Fish", value=f"🔹 {staticdata.load['fish_rarity'][rarity]['cost']} silver", inline=True)
			return await ctx.send(embed=embed)
		else:
			embed = discord.Embed(title="__**B W E K H S H O P**__", description="List of all the things you can sell for money!", color=0x2FB7EA)
			embed.add_field(name=">pawnshop 1", value="Fish", inline=True)
			return await ctx.send(embed=embed)

	@commands.command()
	async def buy(self, ctx, cmd=None, amount=1):
		'''Buy an item! See listings with >shop'''
		def check_money(user, cost):
			if user.data["money"]["silver"] >= cost:
				return True
			return False

		user = User(ctx.guild, ctx.message.author)

		if cmd.lower() in staticdata.load["shop"]["fish items"]["items"]:
			item = cmd.lower()
			if item == "boat":
				if item in user.data['fish_upgrades']:
					return await ctx.send("You already have a boat.")
				cost = staticdata.load["shop"]["fish items"]["items"][item]["cost"]
				if check_money(user, cost) == True:
					user.data['money']['silver'] -= cost
					user.data['fish_upgrades'].append("boat")
					return await ctx.send(f"Successfully bought a {item} for {cost} silver.")
				else:
					return await ctx.send("You do not have enough silver.")

			cost = staticdata.load["shop"]["fish items"]["items"][item]["cost"] * abs(amount)

			if check_money(user, cost) == True:
				addItem(user.inven, item, amount)
				user.data['money']['silver'] -= cost
				data.save()
				return await ctx.send(f"Successfully bought {amount} {item} for {cost} silver.")
			return await ctx.send("You do not have enough silver.")

		elif cmd.lower() in staticdata.load["shop"]["aquarium"]["items"]:
			item = cmd.lower()
			cost = staticdata.load["shop"]["aquarium"]["items"][item]["cost"] 
			if item == "expansion":
				if str(amount) in user.data["aquarium"]:
					aquarium = user.data["aquarium"][str(amount)]
				else:
					return await ctx.send("Please type the aquarium number you wish to expand. `>buy expansion 2`")

				if aquarium["slots"] >= 4:
					return await ctx.send("You've reached the max number of expansions for this aquarium!\n`>buy expansion <aquarium number>`")

				if check_money(user, cost) == True:
					aquarium["slots"] +=1
					user.data['money']['silver'] -= cost
					data.save()
					return await ctx.send(f"Successfully expanded your aquarium for {cost} silver.")
				return await ctx.send("You do not have enough silver.")
			elif item == "aquarium":
				if len(user.data["aquarium"]) > 5:
					return await ctx.send("You've reached the max amount of aquariums.")
				if check_money(user, cost) == True:
					user.data['money']['silver'] -= cost
					num = len(user.data["aquarium"]) + 1
					user.data["aquarium"][str(num)] = {}
					user.data["aquarium"][str(num)]["decor"] = "sand"
					user.data["aquarium"][str(num)]["fish"] = []
					user.data["aquarium"][str(num)]["slots"] = 2
					data.save()
					return await ctx.send(f"Successfully bought a new aquarium for {cost} silver.\n`>aq list`")
				return await ctx.send("You do not have enough silver.")
			if str(amount) in user.data["aquarium"]:
				aquarium = user.data["aquarium"][str(amount)]
			else:
				return await ctx.send("Please type the aquarium number you wish to buy the decor for. `>buy <decor> 1`")
			if check_money(user, cost) == True:
				aquarium["decor"] = item
				user.data['money']['silver'] -= cost
				data.save()
				return await ctx.send(f"Successfully bought {item} for {cost} silver.")
			return await ctx.send("You do not have enough silver.")
		elif cmd.lower() in staticdata.load["shop"]["ingredients"]["items"]:
			item = cmd.lower()
			cost = staticdata.load["shop"]["ingredients"]["items"][item]["cost"] * abs(amount)
			if check_money(user, cost) == True:
				addItem(user.inven["ingredients"], item, amount)
				user.data['money']['silver'] -= cost
				data.save()
				return await ctx.send(f"Successfully bought {abs(amount)} {item} for {cost} silver.")
			else:
				return await ctx.send("You do not have enough silver.")

	@commands.command()
	async def sell(self, ctx, amount:int=1, *, item=None):
		'''Sell your fish! >sell <amount> <fish name>
		You can check how much each fish is worth in >pawnshop 1'''
		user = User(ctx.guild, ctx.message.author)
		if item == None:
			return await ctx.send("Please enter the amount you want to sell followed by the fish name.")

		if item.lower() in user.inven['fish']:
			fish = item.lower()
			amount = abs(amount)

			if user.inven["fish"][fish] >= amount:
				for fishie in staticdata.load["fish"]:
					if fishie == fish:
						silver = staticdata.load["fish_rarity"][staticdata.load["fish"][fishie]["rarity"]]["cost"] * amount
						break
				subtractItem(user.inven["fish"], fish, amount)
				user.data['money']['silver'] += silver

				data.save()
				return await ctx.send(f"Successfully sold {amount} {fish} for {silver} silver.")
			return await ctx.send("You do not have enough of that fish.")
		elif item.lower() in user.inven['dishes']:
			dish = item.lower()
			amount = abs(amount)
			if user.inven["dishes"][dish] >= amount:
				for recipe in staticdata.load["recipes"]:
					if recipe == dish:
						silver = staticdata.load["recipes"][dish]["cost"] * amount
						break
				subtractItem(user.inven["dishes"], dish, amount)
				user.data['money']['silver'] += silver

				data.save()
				return await ctx.send(f"Successfully sold {amount} {dish} for {silver} silver.")
		return await ctx.send("You do not have that item.")

	@commands.command()
	async def sellall(self, ctx, item = None):
		'''Sell all of an item type.'''
		user = User(ctx.guild, ctx.message.author)
		if item == None:
			return await ctx.send("Please enter item type you want to sell all of. `>sellall <insert item type>`")

		if item.lower() == "fish":
			silver = 0
			for fish in user.inven['fish']:
				amount = user.inven['fish'][fish]

				for fishie in staticdata.load["fish"]:
					if fish == fishie:
						silver += staticdata.load["fish_rarity"][staticdata.load["fish"][fish]["rarity"]]["cost"] * amount
						break

			user.data['money']['silver'] += silver
			user.inven["fish"].clear()
			data.save()
			return await ctx.send(f"Successfully sold all fish for {silver} silver.")
		if item.lower() == "dishes":
			silver = 0
			for dish in user.inven['dishes']:
				amount = user.inven['dishes'][dish]

				for recipe in staticdata.load["recipes"]:
					if dish == recipe:
						silver += staticdata.load["recipes"][recipe]["cost"] * amount
						break

			user.data['money']['silver'] += silver
			user.inven["dishes"].clear()
			data.save()
			return await ctx.send(f"Successfully sold all dishes for {silver} silver.")



	@commands.command()
	async def open(self, ctx, *, chest=None):
		user = User(ctx.guild, ctx.message.author)
		if chest == None:
			return await ctx.send("Please enter the chest name you want to open.")

		if chest.lower() in user.inven['chests']:
			if 'key' in user.inven:
				if user.inven['key'] - 1 == 0:
					del user.inven["key"]
				else:
					user.inven['key'] -=1

				chest = chest.lower()
				if user.inven["chests"][chest] >= 1:
					if user.inven["chests"][chest] - 1 == 0:
						del user.inven["chests"][chest]
					else:
						user.inven["chests"][chest] -= 1
				
				loot = random.choice(staticdata.load["chests"][chest]["loot"])

				for index in range(len(loot)):
					for key in loot[index]:
						if key == "silver":
							user.data['money']['silver'] += loot[index][key]
						elif key == "bait":
							if not 'bait' in user.inven:
								user.inven['bait'] = loot[index][key]
							else:
								user.inven['bait'] += loot[index][key]
						elif key == "key":
							if not 'key' in user.inven:
								user.inven['key'] = loot[index][key]
							else:
								user.inven['key'] += loot[index][key]
						elif key == "seaweed":
							addItem(user.inven["ingredients"], key, loot[index][key])
						else:
							if not key in user.inven["chests"]:
								user.inven['chests'][key] = loot[index][key]
							else:
								user.inven['chests'][key] += loot[index][key]
						data.save()
						await ctx.send(f"You opened a {chest}... and got {loot[index][key]} {key}!")
			else:
				return await ctx.send(f"You don't have any keys. Check `>shop` for more.")
		else:
			return await ctx.send("You don't own that chest.")



def setup(bot):
	bot.add_cog(Shop(bot))