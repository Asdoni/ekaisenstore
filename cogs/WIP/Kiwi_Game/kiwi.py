import json
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
from discord import Member
import os

def is_allowed_role(ctx):
    allowed_roles = ['Admin', 'Best Egirls']
    user_roles = [role.name for role in ctx.user.roles]
    return any(role in user_roles for role in allowed_roles)

prefix = os.environ.get('PREFIX')

try:
    with open('cogs/Kiwi_Game/pets.json', 'r') as pet_file:
        pet_data = json.load(pet_file)
except (FileNotFoundError, json.JSONDecodeError):
    pet_data = {}

try:
    with open('cogs/Kiwi_Game/shop.json', 'r') as shop_file:
        shop_data = json.load(shop_file)
except (FileNotFoundError, json.JSONDecodeError):
    shop_data = {}

class Kiwi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pet_variables = {}

    @app_commands.command(
            name="adopt",
            description="Adopt a pet"
    )
    @commands.check(is_allowed_role)
    @app_commands.choices(sex=[Choice(name="Male", value="Male"), Choice(name="Female", value="Female")])
    async def adiot(self, ctx, pet_name: str, sex: str):
        pattern = r'^[a-zA-Z0-9_]+$'
        if ' ' in pet_name or '@' in pet_name:
            await ctx.response.send_message("Invalid pet name. Please do not use spaces or mentions.")
            return

        with open('cogs/Kiwi_Game/config.json') as config_file:
            config_data = json.load(config_file)
            available_sex = config_data.get("Sex")

        if sex not in available_sex:
            await ctx.send("Invalid sex. Please select a valid sex from the options: Male, Female.")
            return

        for user_id, pet_info in self.pet_variables.items():
            if pet_info['name'] == pet_name:
                await ctx.send(f"{pet_name} is already adopted by another user!")
                return

        user_id = str(ctx.user.id)
        self.pet_variables[user_id] = {
            'name': pet_name,
            'sex': sex,
            'level': 1
        }
        await ctx.response.send_message(f"You adopted a {sex} {pet_name} for free!")

        with open('cogs/Kiwi_Game/pets.json', 'w') as pet_file:
            json.dump(self.pet_variables, pet_file, indent=4)

    @app_commands.command(
            name="buy_pet",
            description="Buy a pet"
        )
    async def buy_pet(self, ctx, pet_name: str):
        if pet_name in pet_data:
            user_id = str(ctx.user.id)
            if user_id in pet_data and pet_data[user_id] is not None:
                await ctx.response.send_message("You already have a pet!")
            else:
                pet_data[user_id] = {
                    'name': pet_name,
                    'level': 1
                }
                await ctx.response.send_message(f"You bought a {pet_name}!")
                with open('pets.json', 'w') as pet_file:
                    json.dump(pet_data, pet_file, indent=4)
        else:
            await ctx.response.send_message("That pet doesn't exist!")

    # Command to buy an item from the shop
    @app_commands.command(
            name="buy_item",
            description="Buy an item from the shop"
        )
    async def buy_item(self, ctx, item_name: str):
        # Check if the item is available in the shop data
        if item_name in shop_data:
            # Get the user's ID
            user_id = str(ctx.user.id)

            # Check if the user has enough currency to buy the item
            if 'currency' in pet_data[user_id] and pet_data[user_id]['currency'] >= shop_data[item_name]['price']:
                # Subtract the price of the item from the user's currency
                pet_data[user_id]['currency'] -= shop_data[item_name]['price']

                # Add the item to the user's inventory
                if 'inventory' not in pet_data[user_id]:
                    pet_data[user_id]['inventory'] = []
                pet_data[user_id]['inventory'].append(item_name)

                await ctx.response.send_message(f"You bought a {item_name}!")

                # Save the pet data to the JSON file
                with open('pets.json', 'w') as pet_file:
                    json.dump(pet_data, pet_file, indent=4)
            else:
                await ctx.response.send_message("You don't have enough currency!")
        else:
            await ctx.response.send_message("That item doesn't exist!")

    # Command to increase the pet's level
    @app_commands.command(
            name="pet_level",
            description="Increase the pet's level"
        )
    async def pet_level(self, ctx):
    # Get the user's ID
        user_id = str(ctx.user.id)
        
        # Print the user's ID for debugging
        print(f"User ID: {user_id}")

        # Check if the user has a pet
        if user_id in pet_data and pet_data[user_id] is not None:
            # Get the last level up time for the pet
            last_level_up = pet_data[user_id].get('last_level_up')

            # Check if the pet can level up
            if last_level_up is None or (datetime.datetime.now() - datetime.datetime.fromisoformat(last_level_up)).days >= 1:
                # Increase the pet's level
                pet_data[user_id]['level'] += 1

                # Update the last level up time
                pet_data[user_id]['last_level_up'] = datetime.datetime.now().isoformat()

                await ctx.response.send_message("Pet leveled up!")
            else:
                await ctx.response.send_message("You can only level up your pet once per day!")
        else:
            await ctx.response.send_message("You don't have a pet!")

    @app_commands.command(
            name="stats",
            description="View your pet's stats"
        )
    async def view_pet_stats(self, ctx, user: Member):
        # Get the user's ID
        user_id = str(ctx.user.id)

        # Load the pet data from the JSON file
        try:
            with open('cogs/Kiwi_Game/pets.json', 'r') as pet_file:
                pet_data = json.load(pet_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle the case when the file is missing or empty
            pet_data = {}

        # Check if a specific user is mentioned
        if user is not None:
            # Get the mentioned user's ID
            user_id = str(user.id)

        # Check if the user has a pet
        if user_id in pet_data and pet_data[user_id] is not None:
            pet_name = pet_data[user_id]['name']
            pet_level = pet_data[user_id]['level']
            await ctx.response.send_message(f"<@{user_id}>'s pet: {pet_name} (Level {pet_level})")
        else:
            await ctx.response.send_message(f"<@{user_id}> doesn't have a pet!")

def setup(bot):
    bot.add_cog(Kiwi(bot))