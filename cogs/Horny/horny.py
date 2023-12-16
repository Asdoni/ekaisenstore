import io
from math import pi, cos, sin
from random import randint

from PIL import Image, ImageDraw
from discord import app_commands, Embed, File
from discord.ext import commands

from bot import EGirlzStoreBot


class HornyCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="horny",
        description="Check your horny level"
    )
    @app_commands.checks.cooldown(1, 86400)  # 86400 24h
    async def horny(self, ctx):
        user = ctx.user

        horny_percentage = randint(1, 100)
        resulting_image = self.generate_percentage_image_full_image(user.display_avatar.url, horny_percentage)
        byte_array = io.BytesIO()
        resulting_image.save(byte_array, format='PNG')
        byte_array.seek(0)

        # Create an embed for a richer user experience
        embed = Embed(
            title=f"{user.name}'s Horny Level",
            description=f"Horny percentage: {horny_percentage}%",
            color=randint(0, 0xFFFFFF),
        )

        # Send the resulting image and the embed as a follow-up
        file = File(byte_array, filename="result.png")

        # Set the image in the embed to the resulting image you've generated
        embed.set_image(url="attachment://result.png")
        await ctx.response.send_message(embed=embed, file=file)

    def generate_percentage_image_full_image(self, base_image_url, horny_percentage):
        # Download the image from the URL
        response = self.bot.http_session.get(base_image_url, timeout=5)
        response.raise_for_status()
        # Create an in-memory image from the downloaded content
        base_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
        width, height = base_image.size
        mask = Image.new("L", (width, height), 0)
        # Draw the slice
        ImageDraw.Draw(mask).polygon(create_circle_points(width, height, horny_percentage), fill=255)
        base_image.putalpha(mask)
        return base_image


def create_circle_points(width: int, height: int, percent: int, amount=100):
    radius = min(width, height) // 2
    angle = 2 * pi * (percent / 100)
    center_x, center_y = width // 2, height // 2
    points = [(center_x, center_y)]
    for i in range(int(angle * amount)):  # an arbitrary large number for accuracy
        theta = pi / 2 - i * 0.01  # start from the top-middle
        x = center_x + radius * cos(theta)
        y = center_y - radius * sin(theta)
        points.append((x, y))
    points.append((center_x, center_y))
    return points


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(HornyCog(bot))
