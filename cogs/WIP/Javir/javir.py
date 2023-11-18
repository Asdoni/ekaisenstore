import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import json
import asyncio

# Load scores from javir.json
def load_scores():
    try:
        with open('cogs/Javir/javir.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save scores to javir.json
def save_scores(data):
    with open('cogs/Javir/javir.json', 'w') as f:
        json.dump(data, f)

def format_timedelta(td):
    # Extract days, seconds and microseconds from timedelta
    days, seconds = td.days, td.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"

class Javir(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def check_cooldown(self, user_id):
        max_uses_per_day = 10
        cooldown_time = timedelta(seconds=86400)
        current_time = datetime.utcnow()

        if user_id in self.cooldowns:
            last_used, count = self.cooldowns[user_id]

            # Check if we're in a new day since last use
            if current_time - last_used > cooldown_time:
                self.cooldowns[user_id] = (current_time, 1)  # reset count
                return True, None

            # Check if the user has exceeded their uses for the day
            elif count >= max_uses_per_day:
                time_until_reset = cooldown_time - (current_time - last_used)
                return False, time_until_reset

            # If they haven't exceeded, then increment the count and proceed
            else:
                self.cooldowns[user_id] = (last_used, count + 1)
                return True, None

        # If the user is not in the cooldowns dictionary, add them
        else:
            self.cooldowns[user_id] = (current_time, 1)  # initialize count
            return True, None

    def get_user_data(self, user_id):
        scores = load_scores()
        return scores.get(str(user_id), {"value": 0, "tries": 0, "successes": 0})

    def set_user_data(self, user_id, value, tries=None, successes=None):
        scores = load_scores()
        # If tries or successes are not provided, default to existing values
        tries = tries if tries is not None else scores.get(str(user_id), {}).get("tries", 0)
        successes = successes if successes is not None else scores.get(str(user_id), {}).get("successes", 0)

        user_data = {
            "value": value,
            "tries": tries,
            "successes": successes
        }
        scores[str(user_id)] = user_data
        save_scores(scores)


    @app_commands.command(
        name="javir",
        description="Upgrade your items!"
    )
    async def javir(self, ctx):
        user_id = ctx.user.id

        # Check for cooldown
        is_allowed, time_remaining = await self.check_cooldown(user_id)
        if not is_allowed:
            formatted_time_remaining = format_timedelta(time_remaining)
            await ctx.response.send_message(f"You're on cooldown! Try again in {formatted_time_remaining}.")
            return
        
        user_data = self.get_user_data(user_id)
        current_value = user_data["value"]
        tries = user_data["tries"] + 1
        successes = user_data["successes"]  # Initialize successes

        # Check if item is at max
        if current_value == 100:
            description = "Your item is at max!"
            embed_color = discord.Color.blue()
        else:
            # 50% chance for success/failure
            success = random.choice([True, False])

            if success:
                current_value += 1
                successes += 1  # Increment successes
                description = f"Success! Your item has been upgraded to {current_value}."
                embed_color = discord.Color.green()
            else:
                current_value = max(0, current_value - 1)
                description = f"Failed! Your item has been downgraded to {current_value}."
                embed_color = discord.Color.red()
        
        self.set_user_data(user_id, current_value, tries, successes)
        
        embed = discord.Embed(description=description, color=embed_color)
        await ctx.response.send_message(embed=embed)


    @app_commands.command(
        name="javirleaderboard",
        description="Show Javir leaderboard!"
    )
    async def leaderboard(self, ctx):
        # Load the latest scores
        scores = load_scores()

        # Sort scores by item value in descending order
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]["value"], reverse=True)

        embed = discord.Embed(
            title="Javir Leaderboard",
            color=random.randint(0, 0xFFFFFF)  # Random color
        )

        for idx, (user_id, data) in enumerate(sorted_scores, 1):
            user = await self.bot.fetch_user(int(user_id))
            user_name = user.display_name
            success_rate = (data['successes'] / data['tries']) * 100 if data['tries'] != 0 else 0
            embed.add_field(name=f"{idx}. {user_name}",
                            value=f"Item: {data['value']} | Tries: {data['tries']} | Success Rate: {success_rate:.2f}%",
                            inline=False)

        await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name="javirrank",
        description="Show your own Javir stats!"
    )
    async def rank(self, ctx):
        user_id = ctx.user.id
        user_data = self.get_user_data(user_id)
        user_name = ctx.user.display_name

        success_rate = (user_data['successes'] / user_data['tries']) * 100 if user_data['tries'] != 0 else 0

        embed = discord.Embed(
            title=f"{user_name}'s Javir Stats",
            description=f"Item: {user_data['value']} | Tries: {user_data['tries']} | Success Rate: {success_rate:.2f}%",
            color=random.randint(0, 0xFFFFFF)
        )

        await ctx.response.send_message(embed=embed)    

def setup(bot):    
    bot.add_cog(Javir(bot))