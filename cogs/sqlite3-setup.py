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
            warning_log int
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
                    warn_id int NOT NULL UNIQUE, --incr
                    rule int DEFAULT 0,
                    description text DEFAULT 'None',

                    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                    )""")

    @commands.command(name="setup")
    async def setup(self, ctx):
        '''Add to database.'''
        embed=discord.Embed(title="Step 1/3", description="""Adding server to table...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        msg = await ctx.send(embed=embed)

        self.c.execute('INSERT OR IGNORE INTO Servers(server_id) VALUES(?)', (ctx.message.guild.id,))
        self.db.commit()

        embed=discord.Embed(title="Step 1/3", description="""✅ Added server to table.
                                                                Adding users...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for member in ctx.message.guild.members:
            self.c.execute('INSERT OR IGNORE INTO Users(user_id) VALUES(?)', (member.id,))
            self.c.execute('INSERT OR IGNORE INTO user_in_server(server_id, user_id) VALUES(?,?)', (ctx.message.guild.id, member.id,))

        self.db.commit()

        embed=discord.Embed(title="Step 1/3", description="""✅ Added server to table.
                                                                ✅ Added users.
                                                                    Adding channels...""", color=0xff0000)
        embed.set_author(name="Setting up database...")
        await msg.edit(embed=embed)

        for channel in ctx.message.guild.channels:
            self.c.execute('INSERT OR IGNORE INTO Channels(server_id, channel_id) VALUES(?,?)', (ctx.message.guild.id, channel.id,))

        self.db.commit()

        embed=discord.Embed(title="Step 2/3", description="""✅ Added server to table.
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

        self.c.execute('SELECT channel_id FROM Channels WHERE server_id=? AND channel_id=?', (ctx.message.guild.id, channel_id))
        waiting_room = self.c.fetchone()
        if waiting_room == None:
           return await ctx.send("No such channel exists. Please redo the command.")

        self.c.execute('UPDATE Servers SET waiting_room=? WHERE server_id=?', (waiting_room[0], ctx.message.guild.id))
        self.db.commit()

        waiting_room = self.bot.get_channel(waiting_room[0])

        embed=discord.Embed(title="Step 3/3", description=f"""✅ Added server to table.
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

        self.c.execute('SELECT channel_id FROM Channels WHERE server_id=? AND channel_id=?', (ctx.message.guild.id, channel_id))
        waiting_log = self.c.fetchone()
        if waiting_log == None:
           return await ctx.send("No such channel exists. Please redo the command.")

        self.c.execute('UPDATE Servers SET waiting_log=? WHERE server_id=?', (waiting_log[0], ctx.message.guild.id))
        self.db.commit()

        waiting_log = self.bot.get_channel(waiting_log[0])

        embed=discord.Embed(title="Step 3/3", description=f"""✅ Added server to table.
                                                                ✅ Added users.
                                                                    ✅ Added channels.
                                                                        ✅ {waiting_room.mention} set as waiting room.
                                                                            ✅ {waiting_log.mention} set as waiting log.""", color=0x00FF00)
        embed.set_author(name="Done!")
        await msg.edit(embed=embed)

        #MISSING WARNING LOG CHANNEL

        
        

def setup(bot):
    bot.add_cog(Sqlite3(bot))