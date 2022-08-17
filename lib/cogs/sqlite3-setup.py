import os
import sqlite3
import discord
from discord.ext import commands

from ..db import db

class Sqlite3(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup")
    async def setup(self, ctx):
        '''Add to database.'''
        embed=discord.Embed(title="Step 1/5", description="""Adding server to table...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        msg = await ctx.send(embed=embed)

        db.execute('INSERT OR IGNORE INTO Servers(server_id) VALUES(?)', ctx.message.guild.id)

        embed=discord.Embed(title="Step 1/5", description="""✅ Added server to table.
                                                                Adding users...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for member in ctx.message.guild.members:
            db.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', member.id)
            db.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', ctx.message.guild.id, member.id)


        embed=discord.Embed(title="Step 1/5", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    Adding channels...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for channel in ctx.message.guild.channels:
            db.execute('INSERT OR IGNORE INTO Channels(server_id, channel_id) VALUES(?,?)', ctx.message.guild.id, channel.id)

        embed=discord.Embed(title="Step 2/5", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        embed.add_field(name="Please enter the channel id of your **waiting room**.", value="‎", inline=False)
        await msg.edit(embed=embed)

        def check(m):
            return m.author == ctx.message.author

        user_message = await self.bot.wait_for('message', check=check)

        try:
            channel_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a channel id. Please redo the command.")

        waiting_room = self.bot.get_channel(channel_id)
        if channel == None:
            return await ctx.send("Error: No such channel exists. Please redo the command.")

        db.execute('UPDATE Servers SET waiting_room=? WHERE server_id=?', channel_id, ctx.message.guild.id)

        waiting_room = self.bot.get_channel(channel_id)

        embed=discord.Embed(title="Step 3/5", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        embed.add_field(name="Please enter the channel id of your **waiting log**.", value="‎", inline=False)
        await msg.edit(embed=embed)

        user_message = await self.bot.wait_for('message', check=check)

        try:
            channel_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a channel id. Please redo the command.")

        waiting_log = self.bot.get_channel(channel_id)
        if channel == None:
            return await ctx.send("Error: No such channel exists. Please redo the command.")

        db.execute('UPDATE Servers SET waiting_log=? WHERE server_id=?', channel_id, ctx.message.guild.id)

        waiting_log = self.bot.get_channel(channel_id)

        embed=discord.Embed(title="Step 4/5", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        embed.add_field(name="Please enter the channel id of your **warning log**.", value="‎", inline=False)
        await msg.edit(embed=embed)

        user_message = await self.bot.wait_for('message', check=check)

        try:
            channel_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a channel id. Please redo the command.")

        warning_log = self.bot.get_channel(channel_id)
        if channel == None:
            return await ctx.send("Error: No such channel exists. Please redo the command.")

        db.execute('UPDATE Servers SET warning_log=? WHERE server_id=?', channel_id, ctx.message.guild.id)

        warning_log = self.bot.get_channel(channel_id)

        embed=discord.Embed(title="Step 5/5", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log.
                                                                                ✅ {warning_log.mention} set as warning log.""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        embed.add_field(name="Please enter the role id of your **member role**.", value="‎", inline=False)
        await msg.edit(embed=embed)

        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        member_role = ctx.message.guild.get_role(role_id)
        if member_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET member_role=? WHERE server_id=?', role_id, ctx.message.guild.id)


        embed=discord.Embed(title="Step 5/5", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log.
                                                                                ✅ {warning_log.mention} set as warning log.
                                                                                    ✅ {member_role.mention} set as member role.""", color=0x00FF00)
        embed.set_author(name="Done!")
        await msg.edit(embed=embed)

        #MISSING WARNING LOG CHANNEL


    @commands.command(name="settings")
    async def settings(self, ctx):

        waiting_room = self.bot.get_channel(db.get_one('SELECT waiting_room FROM Servers WHERE server_id=?', ctx.message.guild.id))
        waiting_log = self.bot.get_channel(db.get_one('SELECT waiting_log FROM Servers WHERE server_id=?', ctx.message.guild.id))
        member_role = ctx.message.guild.get_role(db.get_one('SELECT member_role FROM Servers WHERE server_id=?', ctx.message.guild.id))
        codeword = db.get_one('SELECT codeword FROM Servers WHERE server_id=?', ctx.message.guild.id)

        embed=discord.Embed(title="Server Settings", description=f"""Codeword: {codeword}
                                                                        Waiting Room: {waiting_room.mention}
                                                                        Waiting Log: {waiting_log.mention}
                                                                        Member Role: {member_role.mention} 
                                                                    """, color=0x00FF00)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Sqlite3(bot))