import random

import discord
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot


class Throw(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.throw_items = []

    async def load_throw_items(self, guild_id):
        items = await self.bot.db.fetchall(f"SELECT item FROM throw_items WHERE guild_id = {guild_id} OR guild_id = 0")
        return [item[0] for item in items]

    async def save_throw_items(self, guild_id, item):
        await self.bot.db.commit("INSERT INTO throw_items (guild_id, item) VALUES (%s, %s)", (guild_id, item))

    async def remove_throw_items(self, guild_id, item):
        await self.bot.db.commit("DELETE FROM throw_items WHERE guild_id = %s AND item = %s", (guild_id, item))

    async def item_exists_in_db(self, guild_id, item):
        res = await self.bot.db.fetchone("SELECT 1 FROM throw_items WHERE guild_id = %s AND item = %s", (guild_id, item))
        return bool(res)

    @app_commands.command(
        name="throw-item",
        description="Throw an item at a user"
    )
    async def throw_item(self, ctx, user: discord.User):
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
                target_name = user.display_name or user.name

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
    async def add_item(self, ctx, *, item: str):
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
    async def remove_item(self, ctx, *, item: str):
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

    @add_item.error  # Replace `additem` with the actual name of your command function
    async def additem_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")

    @remove_item.error  # Replace `additem` with the actual name of your command function
    async def removeitem_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Throw(bot))
