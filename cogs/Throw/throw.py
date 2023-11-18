import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import AppCommandError
import random
import aiomysql
import os

class Throw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.pool = None
        self.loop.create_task(self.init_db_pool())
        self.throw_items = []

    async def init_db_pool(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=os.environ.get('DB_HOST'),
                port=3306,
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                db=os.environ.get('DB_NAME'),
                loop=self.loop
            )
            print("DB pool initialized successfully")
        except Exception as e:
            print(f"Failed to initialize DB pool: {e}")

    async def load_throw_items(self, guild_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Load items specific to this guild and items available for all guilds (guild_id=0)
                await cur.execute("SELECT item FROM throw_items WHERE guild_id = %s OR guild_id = 0", (guild_id,))
                items = await cur.fetchall()

        return [item[0] for item in items]

    async def save_throw_items(self, guild_id, item):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO throw_items (guild_id, item) VALUES (%s, %s)", (guild_id, item))
                await conn.commit()

    async def remove_throw_items(self, guild_id, item):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM throw_items WHERE guild_id = %s AND item = %s", (guild_id, item))
                await conn.commit()

    async def item_exists_in_db(self, guild_id, item):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 FROM throw_items WHERE guild_id = %s AND item = %s", (guild_id, item))
                result = await cur.fetchone()
                return bool(result)


    @app_commands.command(
        name="throw",
        description="Throw an item at a user"
    )
    async def Throw(self, ctx, user: discord.User):
        try:
            # Acknowledge the command interaction
            await ctx.response.defer()

            self.throw_items = await self.load_throw_items(ctx.guild.id)
            

            if not self.throw_items:
                await ctx.followup.send(content="The item list is empty. Please contact the bot owner to add items.")
                return


            if user is None:
                await ctx.followup.send(content="Please specify a user to throw the item at.")
                return
            else:
                rng = random.randint(1, 1000)
                
                # Get thrower name based on priority: name, nick, display_name
                thrower_name = ctx.user.display_name or ctx.user.nick or ctx.user.name
                # Get target name based on priority: name, nick, display_name
                target_name = user.display_name or user.nick or user.name

                if rng <= 1:
                    # Quintuple throw
                    items = [random.choice(self.throw_items) for _ in range(5)]
                    resp = f"HYPER THROW! Threw **{', '.join(items)}** at **{target_name}**"
                elif rng <= 25:
                    # Triple throw
                    items = [random.choice(self.throw_items) for _ in range(4)]
                    resp = f"GIGA THROW! Threw **{', '.join(items)}** at **{target_name}**"
                elif rng <= 50:
                    # Triple throw
                    items = [random.choice(self.throw_items) for _ in range(3)]
                    resp = f"MEGA THROW! Threw **{', '.join(items)}** at **{target_name}**"
                elif rng <= 150:
                    # Double throw
                    items = [random.choice(self.throw_items) for _ in range(2)]
                    resp = f"DOUBLE THROW! Threw **{', '.join(items)}** at **{target_name}**"
                else:
                    # Single throw
                    item_to_throw = random.choice(self.throw_items)
                    resp = f"Threw **{item_to_throw}** at **{target_name}**"

                await ctx.followup.send(content=f"**{thrower_name}** {resp}")
        except Exception as e:
            print(f"An error occurred in the throw command: {e}")

    @app_commands.command(
        name="additem",
        description="Add an item to the throw list"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def AddItem(self, ctx, *, item: str):
        await ctx.response.defer()
        try:           
            if not item:
                await ctx.followup.send("Please provide a valid item text to add.")
                return

            self.throw_items = await self.load_throw_items(ctx.guild.id)
            
            if item in self.throw_items:
                await ctx.followup.send(f"Item '{item}' already exists in the throw list.")
                return

            await self.save_throw_items(ctx.guild.id, item)
            await ctx.followup.send(f"Item '{item}' has been added to the throw list.")
        except Exception as e:
            print(f"An error occurred in the AddItem command: {e}")

    @app_commands.command(
        name="removeitem",
        description="Remove an item from the throw list"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def RemoveItem(self, ctx, *, item: str):
        await ctx.response.defer()
        try:        
            if not item:
                await ctx.followup.send("Please provide the item text to remove.")
                return

            if not await self.item_exists_in_db(ctx.guild.id, item):
                await ctx.followup.send(f"Item '{item}' does not exist in the throw list.")
                return

            await self.remove_throw_items(ctx.guild.id, item)
            await ctx.followup.send(f"Item '{item}' has been removed from the throw list.")
        except Exception as e:
            print(f"An error occurred in the RemoveItem command: {e}")

    @AddItem.error  # Replace `additem` with the actual name of your command function
    async def additem_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")

    @RemoveItem.error  # Replace `additem` with the actual name of your command function
    async def removeitem_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")


def setup(bot):
    bot.add_cog(Throw(bot))