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

        def create_embed(step_no, description, promptname):
            embed=discord.Embed(title=f"Step {step_no}/6", description=description, color=0xff0000)
            embed.set_author(name="Setting up database...")
            embed.add_field(name=f"Please enter the id of your **{promptname}**.", value="‎", inline=False)
            return embed

        embed=discord.Embed(title="Step 1/6", description="""Adding server to table...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        msg = await ctx.send(embed=embed)

        db.execute('INSERT OR IGNORE INTO Servers(server_id) VALUES(?)', ctx.guild.id)

        embed=discord.Embed(title="Step 1/6", description="""✅ Added server to table.
                                                                Adding users...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for member in ctx.guild.members:
            db.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', member.id)
            db.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', ctx.guild.id, member.id)


        embed=discord.Embed(title="Step 1/6", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    Adding channels...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for channel in ctx.guild.channels:
            db.execute('INSERT OR IGNORE INTO Channels(server_id, channel_id) VALUES(?,?)', ctx.guild.id, channel.id)

        description = """✅ Added server to table.\n✅ Added users.\n✅ Added channels."""
        step_no = 1

        embed=create_embed(step_no, description, "waiting room")
        await msg.edit(embed=embed)



        #getting waiting room ID
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

        db.execute('UPDATE Servers SET waiting_room=? WHERE server_id=?', channel_id, ctx.guild.id)

        description += f"\n✅ {waiting_room.mention} set as waiting room."
        step_no+=1

        embed=create_embed(step_no, description, "waiting log")
        await msg.edit(embed=embed)



        #getting waiting log ID
        user_message = await self.bot.wait_for('message', check=check)

        try:
            channel_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a channel id. Please redo the command.")

        waiting_log = self.bot.get_channel(channel_id)
        if channel == None:
            return await ctx.send("Error: No such channel exists. Please redo the command.")

        db.execute('UPDATE Servers SET waiting_log=? WHERE server_id=?', channel_id, ctx.guild.id)

        description += f"\n✅ {waiting_log.mention} set as waiting log"
        step_no +=1

        embed=create_embed(step_no, description, "warning log")
        await msg.edit(embed=embed)



        #getting warning log
        user_message = await self.bot.wait_for('message', check=check)

        try:
            channel_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a channel id. Please redo the command.")

        warning_log = self.bot.get_channel(channel_id)
        if channel == None:
            return await ctx.send("Error: No such channel exists. Please redo the command.")

        db.execute('UPDATE Servers SET warning_log=? WHERE server_id=?', channel_id, ctx.guild.id)

        description += f"\n✅ {warning_log.mention} set as warning log."
        step_no +=1

        embed=create_embed(step_no, description, "member role")
        await msg.edit(embed=embed)



        #get member role id
        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        member_role = ctx.guild.get_role(role_id)
        if member_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET member_role=? WHERE server_id=?', role_id, ctx.guild.id)

        description += f"\n✅ {member_role.mention} set as member role."
        step_no +=1

        embed=create_embed(step_no, description, "active role")
        await msg.edit(embed=embed)



        #get active member role id
        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        active_role = ctx.guild.get_role(role_id)
        if active_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET active_role=? WHERE server_id=?', role_id, ctx.guild.id)

        description += f"\n✅ {active_role.mention} set as active member role."
        step_no +=1

        embed=create_embed(step_no, description, "suspended role")
        await msg.edit(embed=embed)



        #get mod role id
        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        mod_role = ctx.guild.get_role(role_id)
        if mod_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET mod_role=? WHERE server_id=?', role_id, ctx.guild.id)

        description += f"\n✅ {mod_role.mention} set as mod role."
        step_no +=1

        embed=create_embed(step_no, description, "admin role")
        await msg.edit(embed=embed)



        #get admin role id
        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        admin_role = ctx.guild.get_role(role_id)
        if admin_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET admin_role=? WHERE server_id=?', role_id, ctx.guild.id)

        description += f"\n✅ {admin_role.mention} set as admin role."
        step_no +=1

        embed=create_embed(step_no, description, "suspended role")
        await msg.edit(embed=embed)




        #get suspended role
        user_message = await self.bot.wait_for('message', check=check)

        try:
            role_id = int(user_message.content)
        except:
            return await ctx.send("Error: Please enter a role id. Please redo the command.")

        suspended_role = ctx.guild.get_role(role_id)
        if suspended_role == None:
            return await ctx.send("Error: No such role exists. Please redo the command.")

        db.execute('UPDATE Servers SET member_role=? WHERE server_id=?', role_id, ctx.guild.id)

        description += f"\n✅ {suspended_role.mention} set as admin role."
        step_no +=1

        embed=discord.Embed(title=f"Step {step_no}/{step_no}", description=description, color=0x00FF00)
        embed.set_author(name="Done!")
        await msg.edit(embed=embed)



    @commands.command(name="settings")
    async def settings(self, ctx):

        waiting_room = self.bot.get_channel(db.get_one('SELECT waiting_room FROM Servers WHERE server_id=?', ctx.guild.id))
        waiting_log = self.bot.get_channel(db.get_one('SELECT waiting_log FROM Servers WHERE server_id=?', ctx.guild.id))
        member_role = ctx.guild.get_role(db.get_one('SELECT member_role FROM Servers WHERE server_id=?', ctx.guild.id))
        codeword = db.get_one('SELECT codeword FROM Servers WHERE server_id=?', ctx.guild.id)

        embed=discord.Embed(title="Server Settings", description=f"""Codeword: {codeword}
                                                                        Waiting Room: {waiting_room.mention}
                                                                        Waiting Log: {waiting_log.mention}
                                                                        Member Role: {member_role.mention} 
                                                                    """, color=0x00FF00)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Sqlite3(bot))