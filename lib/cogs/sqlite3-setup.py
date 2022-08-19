import os
import sqlite3
import discord
import asyncio
from discord.ext import commands

from ..db import db

class Sqlite3(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup")
    async def setup(self, ctx):
        '''Add to database.'''
        embed=discord.Embed(title="Step 1/6", description="""Adding server to table...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        msg = await ctx.send(embed=embed)

        db.execute('INSERT OR IGNORE INTO Servers(server_id) VALUES(?)', ctx.message.guild.id)

        embed=discord.Embed(title="Step 1/6", description="""✅ Added server to table.
                                                                Adding users...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for member in ctx.message.guild.members:
            db.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', member.id)
            db.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', ctx.message.guild.id, member.id)


        embed=discord.Embed(title="Step 1/6", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    Adding channels...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for channel in ctx.message.guild.channels:
            db.execute('INSERT OR IGNORE INTO Channels(server_id, channel_id) VALUES(?,?)', ctx.message.guild.id, channel.id)

        embed=discord.Embed(title="Step 2/6", description="""✅ Added server to table.
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

        embed=discord.Embed(title="Step 3/6", description=f"""✅ Added server to table.
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

        embed=discord.Embed(title="Step 4/6", description=f"""✅ Added server to table.
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

        embed=discord.Embed(title="Step 5/6", description=f"""✅ Added server to table.
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


        embed=discord.Embed(title="Step 5/6", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log.
                                                                                ✅ {warning_log.mention} set as warning log.
                                                                                    ✅ {member_role.mention} set as member role.""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        embed.add_field(name="Please enter the role id of your **suspended role**.", value="‎", inline=False)
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

        embed=discord.Embed(title="Step 6/6", description=f"""✅ Added server to table.
                                                        ✅ Added users.
                                                            ✅ Added channels.
                                                                ✅ {waiting_room.mention} set as waiting room.
                                                                    ✅ {waiting_log.mention} set as waiting log.
                                                                        ✅ {warning_log.mention} set as warning log.
                                                                            ✅ {member_role.mention} set as member role.
                                                                                ✅ {member_role.mention} set as suspended role.""", color=0x00FF00)

        embed.set_author(name="Done!")
        await msg.edit(embed=embed)



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
    
    @commands.command(name="newcode")  # I thought of a temporary name, feel free to change it to something else
    async def newcode(self, ctx, codeword=None):
        """
        Changes the code word after it has been set. Prompts user to confirm.
        This isn't the most pretty, but it works.
        Usage: >newcode [new codeword]
        :return: None
        """
        if codeword is None:
            # I wanted this to ask for a new code word but its 3AM and im pushing my work for now
            return await ctx.send('Formatting is `>newcode [new code]`. Please re-run the command with the new desired code')
            
            

        # read the code given
        msg = await ctx.send(f'The code word will be changed to "{codeword}". React with ✅ to confirm or ❌ to cancel')

        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        
        # have user confirm or deny
        def check(reaction, user):
            # ???: will this listen to any message reaction or just the one on msg
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            await msg.clear_reactions()
        except asyncio.TimeoutError:
            await ctx.send("Operation timed out. Please re-run the command")
        
        if reaction.emoji == '✅':
            # if True:assign the code to the proper table
            db.execute('''UPDATE Servers SET codeword=? WHERE Servers.server_id=?;''', codeword, ctx.message.guild.id)
            await ctx.send(f'Codeword successfully changed to "{codeword}"')
        elif reaction.emoji == '❌':
            await ctx.send("Action cancelled. Please redo the command.")
        

def setup(bot):
    bot.add_cog(Sqlite3(bot))