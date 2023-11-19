import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta
import io
from PIL import Image, ImageDraw
from math import radians, pi, cos, sin, tan
import requests
from random import randint

def generate_percentage_image_full_image(base_image_url, horny_percentage):
    # Download the image from the URL
    response = requests.get(base_image_url, timeout=5)
    response.raise_for_status()

    # Create an in-memory image from the downloaded content
    base_image = Image.open(io.BytesIO(response.content)).convert("RGBA")  # Convert to RGBA
    
    width, height = base_image.size
    center_x, center_y = width // 2, height // 2

    mask = Image.new("L", (width, height), 0)  # L mode is fine for the mask
    draw = ImageDraw.Draw(mask)

    # Calculate the angle based on the percentage
    angle = (horny_percentage / 100) * 360
    
    radius = min(width, height) // 2
    angle = 2 * pi * (horny_percentage / 100)

    points = [(center_x, center_y)]
    for i in range(int(angle * 100)):  # an arbitrary large number for accuracy
        theta = pi/2 - i * 0.01  # start from the top-middle
        x = center_x + radius * cos(theta)
        y = center_y - radius * sin(theta)
        points.append((x, y))

    # Return to the center to complete the slice
    points.append((center_x, center_y))

    # Draw the slice
    draw.polygon(points, fill=255)

    # Apply the mask to the alpha channel of the base image
    base_image.putalpha(mask)
    return base_image


def format_timedelta(td):
    # Extract days, seconds and microseconds from timedelta
    days, seconds = td.days, td.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"


class HornyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def check_cooldown(self, user_id):
        cooldown_time = timedelta(seconds=86400)
        current_time = datetime.utcnow()

        if user_id in self.cooldowns:
            time_since_last_command = current_time - self.cooldowns[user_id]
            if time_since_last_command < cooldown_time:
                return False, (cooldown_time - time_since_last_command)
            else:
                self.cooldowns[user_id] = current_time
                return True, None
        else:
            self.cooldowns[user_id] = current_time
            return True, None

    @app_commands.command(
        name="horny",
        description="Check your horny level"
    )
    @commands.cooldown(1, 86400, commands.BucketType.member) #86400 24h
    async def horny(self, ctx):
        try:
            user = ctx.user

            is_allowed, time_remaining = await self.check_cooldown(user.id)
            if not is_allowed:
                formatted_time_remaining = format_timedelta(time_remaining)
                await ctx.response.send_message(f"You're on cooldown! Try again in {formatted_time_remaining}.")
                return

            # Generate a random color for the embed
            random_color = randint(0, 0xFFFFFF)
            horny_percentage = random.randint(1, 100)
            
            # Use display_avatar format for avatar
            avatar_url = str(user.display_avatar.with_format('png').url)

            resulting_image = generate_percentage_image_full_image(avatar_url, horny_percentage)
            byte_array = io.BytesIO()
            resulting_image.save(byte_array, format='PNG')
            byte_array.seek(0)
            
            # Create an embed for a richer user experience
            embed = discord.Embed(title=f"{user.name}'s Horny Level", description=f"Horny percentage: {horny_percentage}%", color=random_color)

            # Send the resulting image and the embed as a follow-up
            file = discord.File(byte_array, filename="result.png")

            # Set the image in the embed to the resulting image you've generated
            embed.set_image(url="attachment://result.png")
            await ctx.response.send_message(embed=embed, file=file)

        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.response.send_message("An error occurred. Please try again later.")

def setup(bot):
    bot.add_cog(HornyCog(bot))
