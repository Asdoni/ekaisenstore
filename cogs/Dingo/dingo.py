import asyncio
import json
import os
import random
from datetime import datetime

import discord
import pytz
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot
from oldCommandCustomErrors import is_allowed_guild

# Define the time zone using pytz (e.g., UTC+2)
time_zone = pytz.timezone('Europe/Amsterdam')

# Calculate the time in the desired time zone (e.g., UTC+2)
current_time = datetime.now(time_zone)

# Format the time as HH:MM
current_time_str = current_time.strftime("%H:%M")

# Define a dictionary to store user rolls during the timer
user_rolls = {}


class Dingo(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.is_dingo_timer_active = False
        self.user_rolls = {}  # Use the class-level dictionary

        current_directory = os.path.dirname(os.path.abspath(__file__))
        dingo_json_path = os.path.join(current_directory, 'dingo.json')

        with open(dingo_json_path, 'r') as dingo_file:
            dingo_data = json.load(dingo_file)
            self.dingo_message = dingo_data.get('dingo_message', '')

    @commands.command(name="dingo")
    @commands.has_permissions(administrator=True)
    @is_allowed_guild([1062323948840296459])
    async def dingo(self, ctx):
        self.is_dingo_timer_active = True
        await ctx.message.delete()

        # Clear the user_rolls dictionary for this specific instance
        self.user_rolls.clear()

        role_id = 1062323948987109412  # EGIRLZ ROLE 1062323948987109412
        role = ctx.guild.get_role(role_id)

        if role:
            await ctx.send(role.mention)

        embed = discord.Embed(
            title="Dingo Roll",
            description=self.dingo_message,
            color=discord.Color.random()  # You can change this to a predefined color or generate a random one.
        )

        await ctx.send(embed=embed)

        # Define a list of time intervals in minutes
        time_intervals = [25, 20, 15, 10, 5]

        remaining_time = max(time_intervals)

        while remaining_time > 0:
            if remaining_time in time_intervals:
                await ctx.send(f"**{remaining_time} MINUTE(S) REMAINING**")

            await asyncio.sleep(300)  # Sleep for 5 minutes
            remaining_time -= 5

        await self.display_roll_results(ctx)

        # Reset the timer status to False when the timer is finished
        self.is_dingo_timer_active = False

    async def display_roll_results(self, ctx):
        # After all intervals are done, post the "ROLL CLOSED" message
        def create_embed(title, description, color):
            return discord.Embed(
                title=title,
                description=description,
                color=color
            )

        # Initialize the embed with the title and a color
        roll_closed_embed = create_embed(
            title="ROLL CLOSED",
            description="Collected rolls (from highest to lowest):",
            color=discord.Color.random()
        )

        # Collected rolls dictionary
        collected_rolls = {}

        # Create a list to store the mentioned users' names and roll numbers
        mentioned_users = []

        for user_id, rolls in self.user_rolls.items():  # Use self.user_rolls
            sorted_rolls = sorted(rolls, reverse=True)
            collected_rolls[user_id] = sorted_rolls

        if collected_rolls:
            # Sort the users by their highest roll
            sorted_users = sorted(collected_rolls.keys(), key=lambda user_id: collected_rolls[user_id][0], reverse=True)

            # Function to get the emote based on the roll result
            def get_roll_emote(roll):
                emotes = {
                    (1, 10): "<:andoni:1156911271019552840>",
                    (11, 20): "<:pepePoint:1156906733034295296>",
                    (21, 40): "<:xorinoob:1156912140574277714>",
                    (41, 89): "<:ok:1156913055494586428>",
                    (90, 99): "<:POGGERS:1156906925498310766>",
                    (100, 100): "<a:Peepo_Hacker:1156907116775342131>",
                }

                for (min_range, max_range), emote in emotes.items():
                    if min_range <= roll <= max_range:
                        return emote
                return ""

            embed_field_value = ""
            for user_id in sorted_users:
                user = ctx.guild.get_member(user_id)
                rolls = collected_rolls[user_id]
                rolls_str = ", ".join(map(str, rolls))
                emote = get_roll_emote(rolls[0])
                user_mention = f"<@!{user_id}>"
                roll_info = f"{user_mention} {emote} (Rolls: {rolls_str}) {emote}\n"

                # Check if adding the next user would exceed the field value limit
                if len(embed_field_value) + len(roll_info) > 1024:
                    # Add the field to the current embed
                    roll_closed_embed.add_field(
                        name="Users",
                        value=embed_field_value,
                        inline=False
                    )
                    # Send the current embed and create a new one
                    await ctx.send(embed=roll_closed_embed)
                    roll_closed_embed = create_embed(title="ROLL CLOSED (Continued)", description="",
                                                     color=discord.Color.random())
                    embed_field_value = roll_info  # Start with the next user's info
                else:
                    embed_field_value += roll_info

            # Add any remaining rolls to the last embed
            if embed_field_value:
                roll_closed_embed.add_field(
                    name="Users",
                    value=embed_field_value,
                    inline=False
                )
            await ctx.send(embed=roll_closed_embed)
        else:
            await ctx.send("No rolls were collected during the timer.")

    # Command for users to roll a dice
    @commands.command(name="roll")
    async def roll(self, ctx):
        # Delete the invocation message
        await ctx.message.delete()

        if not self.is_dingo_timer_active:
            error_message = await ctx.send(f"{ctx.author.mention}, you can only roll during the Dingo timer.")
            await asyncio.sleep(5)  # Wait for 5 seconds            
            await error_message.delete()
            return

        # Convert the command to lowercase and check if it matches "roll"
        if ctx.command.qualified_name.lower() != "roll":
            return

        if ctx.author.id not in self.user_rolls:
            self.user_rolls[ctx.author.id] = []  # Initialize an empty list if the user hasn't rolled yet

        if len(self.user_rolls[ctx.author.id]) >= 1:
            error_message = await ctx.send(f"{ctx.author.mention}, you can only roll once during this session.")
            await ctx.message.delete()
            await asyncio.sleep(5)  # Wait for 5 seconds            
            await error_message.delete()
        else:
            random_number = random.randint(1, 100)
            self.user_rolls[ctx.author.id] = [random_number]

            # Define emotes based on the roll result
            emotes = {
                (1, 10): "<:andoni:1156911271019552840>",
                (11, 20): "<:pepePoint:1156906733034295296>",
                (21, 40): "<:xorinoob:1156912140574277714>",
                (41, 89): "<:ok:1156913055494586428>",
                (90, 99): "<:POGGERS:1156906925498310766>",
                (100, 100): "<a:Peepo_Hacker:1156907116775342131>",
            }

            # Find the corresponding emote for the roll result
            emote = next(
                (emote for (min_range, max_range), emote in emotes.items() if min_range <= random_number <= max_range),
                "")

            embed = discord.Embed(
                title="🎲 Roll the Dice 🎲",
                description=f"{emote}  You rolled a {random_number}!  {emote}",
                color=discord.Color.random()
            )

            author_name = ctx.author.display_name
            embed.set_author(name=author_name, icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

    @app_commands.command(
        name="currenttime",
        description="Display the current time in your desired format (UTC+2)."
    )
    async def currenttime(self, ctx):
        try:
            # Acknowledge the command interaction
            await ctx.response.defer()

            # Get the current time in the specified time zone
            current_time = datetime.now(time_zone)
            current_time_str = current_time.strftime("%H:%M")

            await ctx.followup.send(f"The current time is {current_time_str} (UTC+2).")
        except Exception as e:
            await ctx.followup.send("An error occurred while processing your request.")


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Dingo(bot))
