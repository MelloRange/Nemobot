import discord
import json
from discord.ext import commands
from discord.ext import tasks
from globals import *
from random import choice

class Profile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(aliases=['p'])
	async def profile(self, ctx):
		'''Check your profile.
		Aliases: p
		Subcommands:
		`>p <insert username>`
		`>p desc <insert description>`
		`>p color <insert color hexcode>`'''
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

			guild = Guild(ctx.guild)
			
			title = f"{userobject.display_name}'s Profile"
			description = user.profile['description']
			icon = userobject.avatar_url
			color = user.profile['color']
			gold = user.data['money']['gold']
			silver = user.data['money']['silver']
			level = user.data['level']

			embed=discord.Embed(title=title, description=description, color=int(color))
			embed.add_field(name="Level", value=f"{level}", inline=True)
			embed.add_field(name="Money", value=f"🔸{gold} 🔹{silver}", inline=True)
			embed.set_thumbnail(url=icon)
			await ctx.send(embed=embed)

	@profile.command(aliases=['desc'])
	async def description(self, ctx, *, description:str = None):
		user = User(ctx.guild, ctx.message.author)

		if description == None:
			return await ctx.send("Please re-enter the command with a message to change your description.\n`>profile description (insert message)`")

		user.profile['description'] = description
		data.save()
		return await ctx.send("Changed your description!")

	@profile.command()
	async def color(self, ctx, color:str = None):
		user = User(ctx.guild, ctx.message.author)

		if color == None:
			return await ctx.send("Please re-enter the command with a color hexcode.\n`>profile color ffffff`")

		if not match_hex(color):
			return await ctx.send("Please enter a proper hexcode. `EX: ffff000`")
		
		user.profile['color'] = int(color, 16)
		data.save()
		return await ctx.send("Changed your profile color!")


	@commands.group(aliases=['ref', 'r'])
	async def reference(self, ctx):
		'''Pulls up your reference.
		Aliases: ref, r
		Subcommands:
		`>r user <insert username> <opt. insert refname>`
		`>r name <insert refname>`
		`>r delete <insert refname>`'''
		if ctx.invoked_subcommand is None:
			user = User(ctx.guild, ctx.message.author)
			if not user.profile['reference']:
				return await ctx.send("You have no references set! Do `>setref <img attachment or URL>` to set a reference.")

			if "main_reference" in user.profile['reference']:
				return await ctx.send(f"{user.profile['reference']['main_reference']}")
			return await ctx.send(f"{list(user.profile['reference'].values())[0]}")

	@reference.command(aliases=['u'])
	async def user(self, ctx, member = None, refname=None):
		if ctx.invoked_subcommand is None:
			if member == None:
				return await ctx.send("Plesae enter a username.\n`>reference user <username> <opt. refname>")
			else:
				member = finduser(ctx, member)
				if member is None:
					return await ctx.send("Could not find user.")

				user = User(ctx.guild, member)
				if not user.profile['reference']:
					return await ctx.send("This person does not have any references set.")

			if refname == None:
				if "main_reference" in user.profile['reference']:
					return await ctx.send(f"{user.profile['reference']['main_reference']}")
				return await ctx.send(f"{list(user.profile['reference'].values())[0]}")
			else:
				if refname in user.profile['reference']:
					return await ctx.send(f"{user.profile['reference'][refname]}")
				else:
					return await ctx.send(f"This user does not have a ref with the name `{refname}`. Do `>reflist <user>` to see their references.")

	@reference.command(aliases=['n'])
	async def name(self, ctx, refname = None):
		user = User(ctx.guild, ctx.message.author)
		if refname == None:
			return await ctx.send("Please specify a reference name.\n`>reference name <insert name>`")
		else:
			if refname in user.profile['reference']:
				return await ctx.send(f"{user.profile['reference'][refname]}")
			else:
				return await ctx.send(f"You do not have a ref with the name `{refname}`. Do `>reflist` to see your references.")

	@reference.command(aliases=['del', 'd'])
	async def delete(self, ctx, refname = None):
		user = User(ctx.guild, ctx.message.author)
		if refname == None:
			remove_key = user.profile['reference'].pop("main_reference", None)
			if remove_key == None:
				return await ctx.send("No reference to remove.")
			return await ctx.send("Removed main reference.")
		else:
			remove_key = user.profile['reference'].pop(refname, None)
			if remove_key == None:
				return await ctx.send(f"No reference name '{refname}' to remove.")
			return await ctx.send(f"Removed ref '{refname}'.")



	@commands.command(aliases=['setref', 'sr'])
	async def setreference(self, ctx, refname = None, url = None):
		'''Sets your reference to an image or URL.
		Aliases: setref, sr
		Subcommands:
		`>rl <insert refname> <opt. insert url>`'''
		user = User(ctx.guild, ctx.message.author)
		if refname == None:
			if not ctx.message.attachments:
				return await ctx.send("Please attach an image or URL to set it as your reference.")
			else:
				ref = ""
				for attachment in ctx.message.attachments:
					ref += attachment.url + "\n"
				
				user.profile['reference'].update({"main_reference": ref})
				return await ctx.send("Set image as main reference.")
		else:
			if not ctx.message.attachments:
				if url == None:
					url = refname
					user.profile['reference'].update({"main_reference": url})
					return await ctx.send("Set URL as main reference.")
			else:
				url = ""
				for attachment in ctx.message.attachments:
					url += attachment.url + "\n"
			
			user.profile['reference'].update({refname: url})
			return await ctx.send(f"Set image as reference for '{refname}'.")

	@commands.command(aliases=['reflist', 'rl'])
	async def referencelist(self, ctx, user = None):
		'''Shows a user's references..
		Aliases: reflilst, rl
		Subcommands:
		`>sr <insert user>`'''
		if user == None:
			user = User(ctx.guild, ctx.message.author)
			userobject = ctx.message.author
		else: 
			member = finduser(ctx, user)
			if member == None:
				return await ctx.send("Could not find user.")
			user = User(ctx.guild, member)
			userobject = member

		title = f"{userobject.display_name}'s References"
		description = ""
		for reference in user.profile['reference'].keys():
			if reference == "main_reference":
				continue
			description += f"{reference}: {user.profile['reference'][reference]}\n"
		color = user.profile['color']


		embed=discord.Embed(title=title, description=description, color=int(color))

		await ctx.send(embed=embed)

	@commands.command()
	async def pay(self, ctx, user = None, amount:int = None):
		'''Give others your money.'''

		if user == None or amount == None:
			return await ctx.send("Invalid format.\n`>pay <insert user> <insert amount>`")
	
		amount = abs(amount)
		member = finduser(ctx, user)
		if member == None:
			return await ctx.send("Could not find user.")
		selfuser = User(ctx.guild, ctx.message.author)
		user = User(ctx.guild, member)

		def check_money(user, cost):
			if selfuser.data["money"]["silver"] >= cost:
				return True
			return False

		if check_money(user, amount) == True:
			selfuser.data['money']['silver'] -= amount
			user.data['money']['silver'] += amount
			return await ctx.send(f"Gave {member.mention} {amount} silver.")
		else:
			return await ctx.send("You do not have enough money.")

	@commands.command(aliases=['inven', 'inv'])
	async def inventory(self, ctx):
		'''Checks your inventory.
		Aliases: inven, inv'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		title = f"{ctx.message.author.display_name}'s Inventory"
		description = "List of items"
		color = user.profile['color']

		embed=discord.Embed(title=title, description=description, color=int(color))
		othervalue = "\u200b"
		for item in user.inven:
			if item == "chests":
				value = "\u200b"
				for chest in user.inven["chests"]:
					value += f'{chest.capitalize()} x {user.inven["chests"][chest]}\n'
				embed.add_field(name="Chests", value=value, inline=True)
			elif item == "dishes":
				value = "\u200b"
				for dish in user.inven["dishes"]:
					value += f'{staticdata.load["recipes"][dish]["emote"]} {dish.capitalize()} x {user.inven["dishes"][dish]}\n'
				embed.add_field(name="Dishes", value=value, inline=True)
			elif item == "fish":
				value = "\u200b"
				for fish in user.inven["fish"]:
					if len(value) >= 920:
						embed.add_field(name="Fish", value=value, inline=True)
						value = "\u200b"
					value += f'{staticdata.load["fish_rarity"][staticdata.load["fish"][fish]["rarity"]]["emote"]} {staticdata.load["fish"][fish]["emote"]} {fish.capitalize()} x {user.inven["fish"][fish]}\n'
				embed.add_field(name="Fish", value=value, inline=True)
			elif item == "ingredients":
				value = "\u200b"
				for ingredient in user.inven["ingredients"]:
					value += f'{staticdata.load["ingredients"][ingredient]["emote"]} {ingredient.capitalize()} x {user.inven["ingredients"][ingredient]}\n'
				embed.add_field(name="Ingredients", value=value, inline=True)
			else:
				othervalue += f'{item.capitalize()} x {user.inven[item]}\n'
		embed.add_field(name="Other", value=othervalue, inline=True)

		await ctx.send(embed=embed)

	@commands.group(aliases=['aqu', 'aq'])
	async def aquarium(self, ctx, number=None, cmd=None, *, fish=None):
		'''Open your aquarium, or add a fish into it.
		Aliases: aqu, aq
		`>aq list`
		`>aq <insert aquarium number>`
		`>aq <insert aquarium number> add <insert fish name>`
		`>aq <insert aquarium number> remove <insert fish name>`'''
		user = User(ctx.guild, ctx.message.author)
		guild = Guild(ctx.guild)

		def getMessage(fishlist):
			value =""
			length = len(fishlist)
			while(length > 0):
				p = random.random()
				if p < 0.08:
					value += "°ₒ"
				elif p < (1- len(fishlist)*0.1):
					value += "\u3000"
				else:
					gotfish = random.choice(fishlist)
					fishlist.remove(gotfish)
					length -=1

					for fish in staticdata.load["fish"]:
						if fish == gotfish:
							value += staticdata.load["fish"][fish]['emote']
			return value

		def split(a, n):
			k, m = divmod(len(a), n)
			return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))




		if number is None:
			number = "1"

		if number.lower() == "list":
			embed=discord.Embed(title=f"{ctx.message.author.display_name}'s Aquariums", color=int(user.profile["color"]))
			for aquarium in user.data["aquarium"]:
				embed.add_field(name=f'{aquarium}', value=f'Fish: {len(user.data["aquarium"][aquarium]["fish"])}\nDecor: {user.data["aquarium"][aquarium]["decor"]}', inline=False)
			return await ctx.send(embed=embed)

		if number in user.data["aquarium"]:
			aquarium = user.data["aquarium"][number]
		else:
			return await ctx.send("Invalid aquarium number. Do `>aquarium list`.")

		if cmd is None:
			random.shuffle(aquarium["fish"])

			ground = staticdata.load["shop"]["aquarium"]["items"][aquarium["decor"]]["ground"]
			decor1 = staticdata.load["shop"]["aquarium"]["items"][aquarium["decor"]]["decor1"]
			decor2 = staticdata.load["shop"]["aquarium"]["items"][aquarium["decor"]]["decor2"]
			decor3 = staticdata.load["shop"]["aquarium"]["items"][aquarium["decor"]]["decor3"]

			allfish = ", ".join(aquarium["fish"])
			fishrows = split(aquarium["fish"], aquarium["slots"])
			embed=discord.Embed(title=f"{ctx.message.author.display_name}'s Aquarium {number}", color=int(user.profile["color"]))
			embed.add_field(name="\u200b", value="‿︵"*15, inline=True)
			for row in fishrows:
				embed.add_field(name="\u200b", value="\u200b" + getMessage(row), inline=False)
			embed.add_field(name="\u200b", value="\u200b" + ground*1 + decor3*1 + decor2*1 + decor1*4 + ground*6 + decor2*1 + decor1*3 + decor3*1 + ground*1 +  decor2*1 + decor1*2 + ground*1, inline=False)
			embed.add_field(name="Fish", value="\u200b" + allfish, inline=False)
			return await ctx.send(embed=embed)

		elif cmd.lower() == "add":
			if fish ==None:
				return await ctx.send("Please re-enter the command with a fish name.\n`>aquarium 1 add <insert fishname>`")
			if number in user.data["aquarium"]:
				aquarium = user.data["aquarium"][number]
			else:
				return await ctx.send("Not a valid aquarium number.\n`>aq 1 add <insert fishname>`")
			if len(aquarium["fish"]) >= aquarium["slots"] * 10:
				return await ctx.send("You have too many fish in your aquarium!\nRemove one with `>aq <insert number> remove <insert fish name>`")
			if fish.lower() in user.inven["fish"]:
				aquarium["fish"].append(fish.lower())
				subtractItem(user.inven["fish"], fish, 1)
				return await ctx.send(f"Added {fish.lower()} into your aquarium.")
			else:
				return await ctx.send("You don't have that fish. Check with `>inv`")

		elif cmd.lower() == "remove":
			if fish == None:
				return await ctx.send("Please re-enter the command with a fish name.\n`>aquarium 1 remove <insert fishname>`")
			if number in user.data["aquarium"]:
				aquarium = user.data["aquarium"][number]
			else:
				return await ctx.send("Not a valid aquarium number.\n`>aq 1 remove <insert fishname>`")

			if fish.lower() in aquarium["fish"]:
				aquarium["fish"].remove(fish.lower())
				addItem(user.inven["fish"], fish, 1)
				return await ctx.send(f"Removed {fish.lower()} from your aquarium.")
			return await ctx.send("You do not have that fish in your aquarium.")

		else:
			return await ctx.send("Invalid format. Check `>help aquarium` for more.")


def setup(bot):
	bot.add_cog(Profile(bot))