import os
import sqlite3
import discord
from discord.ext import commands

class Sqlite3(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        DB_NAME = "database"
        db_path = os.path.join(os.path.abspath(os.getcwd()), DB_NAME + ".db")
        self.db = sqlite3.connect(db_path)
        self.c = self.db.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS Servers(
            server_id int NOT NULL UNIQUE,
            codeword text DEFAULT 'orange',
            waiting_room int,
            waiting_log int,
            warning_log int,
            member_role int
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS Users(
                    user_id int NOT NULL UNIQUE
                    )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS user_in_server(
                    server_id int NOT NULL,
                    user_id int NOT NULL,
                    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id),
                    UNIQUE(server_id, user_id)
                    )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS Channels(
                    server_id int NOT NULL,
                    channel_id int NOT NULL UNIQUE,
                    is_art bit DEFAULT 0,
                    is_softban bit DEFAULT 0,
                    is_hardban bit DEFAULT 0,
                    FOREIGN KEY (server_id) REFERENCES Servers(server_id)
                    )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS Profiles(
                    server_id int NOT NULL,
                    user_id int NOT NULL,
                    description text DEFAULT '*Type `>desc [insert description]` to add a description!*',
                    color text, -- DEFAULT gray

                    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id),
                    UNIQUE(server_id, user_id)
                    )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS Warns(
                    server_id int NOT NULL,
                    user_id int NOT NULL,
                    warn_id INTEGER PRIMARY KEY AUTOINCREMENT, --incr
                    rule int DEFAULT 0,
                    description text DEFAULT 'None',

                    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                    )""")

    @commands.command(name="setup")
    async def setup(self, ctx):
        '''Add to database.'''
        embed=discord.Embed(title="Step 1/4", description="""Adding server to table...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        msg = await ctx.send(embed=embed)

        self.c.execute('INSERT OR IGNORE INTO Servers(server_id) VALUES(?)', (ctx.message.guild.id,))
        self.db.commit()

        embed=discord.Embed(title="Step 1/4", description="""✅ Added server to table.
                                                                Adding users...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for member in ctx.message.guild.members:
            self.c.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', (member.id,))
            self.c.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', (ctx.message.guild.id, member.id,))

        self.db.commit()

        embed=discord.Embed(title="Step 1/4", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    Adding channels...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for channel in ctx.message.guild.channels:
            self.c.execute('INSERT OR IGNORE INTO Channels(server_id, channel_id) VALUES(?,?)', (ctx.message.guild.id, channel.id,))

        self.db.commit()

        embed=discord.Embed(title="Step 2/4", description="""✅ Added server to table.
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

        self.c.execute('UPDATE Servers SET waiting_room=? WHERE server_id=?', (channel_id, ctx.message.guild.id))
        self.db.commit()

        waiting_room = self.bot.get_channel(channel_id)

        embed=discord.Embed(title="Step 3/4", description=f"""✅ Added server to table.
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

        self.c.execute('UPDATE Servers SET waiting_log=? WHERE server_id=?', (channel_id, ctx.message.guild.id))
        self.db.commit()

        waiting_log = self.bot.get_channel(channel_id)

        embed=discord.Embed(title="Step 4/4", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log""", color=0xff0000)
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

        self.c.execute('UPDATE Servers SET member_role=? WHERE server_id=?', (role_id, ctx.message.guild.id))
        self.db.commit()


        embed=discord.Embed(title="Step 4/4", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log.
                                                                                ✅ {member_role.mention} set as member role.""", color=0x00FF00)
        embed.set_author(name="Done!")
        await msg.edit(embed=embed)

        #MISSING WARNING LOG CHANNEL


    @commands.command(name="settings")
    async def settings(self, ctx):

        def get_waiting_room(guild_id):
            self.c.execute('SELECT waiting_room FROM Servers WHERE server_id=?', (guild_id,))
            waiting_room = self.c.fetchone()
            return waiting_room[0]

        def get_waiting_log(guild_id):
            self.c.execute('SELECT waiting_log FROM Servers WHERE server_id=?', (guild_id,))
            waiting_log = self.c.fetchone()
            return waiting_log[0]

        def get_member_role(guild_id):
            self.c.execute('SELECT member_role FROM Servers WHERE server_id=?', (guild_id,))
            member_role = self.c.fetchone()
            return member_role[0]

        def get_codeword(guild_id):
            self.c.execute('SELECT codeword FROM Servers WHERE server_id=?', (guild_id,))
            codeword = self.c.fetchone()
            return codeword[0]

        waiting_room = self.bot.get_channel(get_waiting_room(ctx.message.guild.id))
        waiting_log = self.bot.get_channel(get_waiting_log(ctx.message.guild.id))
        member_role = ctx.message.guild.get_role(get_member_role(ctx.message.guild.id))
        codeword = get_codeword(ctx.message.guild.id)

        embed=discord.Embed(title="Server Settings", description=f"""Codeword: {codeword}
                                                                        Waiting Room: {waiting_room.mention}
                                                                        Waiting Log: {waiting_log.mention}
                                                                        Member Role: {member_role.mention} 
                                                                    """, color=0x00FF00)
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Sqlite3(bot))