import discord
import json
import os
import random
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Game
import time
import _thread
import threading
import asyncio
import typing
import sys, traceback
import re
import math
from datetime import date


#threading for json files

class User:
	def __init__(self, guild, member):
		self.data = data.load[str(guild.id)]['members'][str(member.id)]
		self.profile = data.load[str(guild.id)]['members'][str(member.id)]['profile']
		self.inven = data.load[str(guild.id)]['members'][str(member.id)]['inventory']
		self.exp = data.load[str(guild.id)]['members'][str(member.id)]['experience']

class Guild:
	def __init__(self, guild):
		self.data = data.load[str(guild.id)]
		self.channels = data.load[str(guild.id)]['channels']
		self.roles = data.load[str(guild.id)]['roles']
		self.members = data.load[str(guild.id)]['members']
		self.world = data.load[str(guild.id)]['world']


class json_helper(object):
	def __init__(self, file):
		self.filename = file
		self.filelock = threading.RLock()
		with open("/python projects/bwekhupdated/ModonlyBwekh/{}".format(file), 'r', encoding='utf-8') as f:
			self.load = json.load(f)

	def save(self):

		with self.filelock:
			with open("/python projects/bwekhupdated/ModonlyBwekh/data.json", 'w', encoding='utf-8') as f:
				json.dump(self.load, f, indent=4, sort_keys=True)
				f.flush()
				os.fsync(f.fileno())

def subtractItem(itemdict, item, amount):
	itemdict[item.lower()] -= amount
	if itemdict[item.lower()] <= 0:
		del itemdict[item.lower()]
	data.save()

def addItem(itemdict, item, amount):
	if not item.lower() in itemdict:
		itemdict[item.lower()] = 0
	itemdict[item.lower()] += amount
	data.save()

def weightedChoice(itemlist, weightlist):
	randomPercent = random.random()
	for x in range(len(itemdict)):
		if randomPercent <= weightlist[x]:
			return itemlist[x]

def match_hex(color):
	match = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color)
	if match:
		return True
	return False

def match_url(url):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',url)
	if urls:
		return True
	return False

def finduser(ctx, user: str):
    if not user.strip():
        return None

    if user.isdigit():
        user = int(user)
    elif user.startswith('<@') and user.index('>') > 0:
        user = user[2:user.index('>')]
        user = int(user[1:] if user[0] == '!' else user)
    
    if type(user) is int:
        return ctx.guild.get_member(user) if ctx.guild else bot.get_user(user)
    elif ctx.guild:
        guild = ctx.guild
        find = guild.get_member_named(user)
        if find != None:
            return find
        else:
            user = user.lower()
            for member in guild.members:
                if user in member.display_name.lower():
                    return member
            for member in guild.members:
                if member.nick:
                    if user in member.name.lower():
                        return member
            return None
    return None

class Timeout(object):
	def __init__(self, timeout):
		self.timeout = timeout
		self.lock = threading.RLock()
		self.users = {}
	def update(self, user):
		with self.lock:
			self.users[user] = time.time()
	def check(self, user):
		with self.lock:
			if user not in self.users:
				return True
			return time.time() - self.users[user] >= self.timeout

message_timeout = Timeout(30)
data = json_helper('data.json')
staticdata = json_helper('staticdata.json')