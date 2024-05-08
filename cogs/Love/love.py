import io
import random

import discord
from PIL import Image
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot


class Love(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="love",
        description="Compare your love"
    )
    async def love(self, interaction: discord.Interaction, user: discord.User):
        if user == interaction.user:
            embed = discord.Embed(
                title="NSFW WARNING",
                description="It's fine to love yourself but do not overdo it, especially here in public.",
                color=0xFF69B4
            )
            await interaction.response.send_message(embed=embed)
            return

        author_avatar = await self.fetch_image(interaction.user.display_avatar.url)
        user_avatar = await self.fetch_image(user.display_avatar.url)

        avatar_size = (128, 128)
        author_image = Image.open(io.BytesIO(author_avatar)).resize(avatar_size)
        user_image = Image.open(io.BytesIO(user_avatar)).resize(avatar_size)

        love_percentage = random.randint(0, 100)
        love_img_name = f"cogs/Love/images/love_{min(10, max(1, love_percentage // 10))}.png"
        love_img = Image.open(love_img_name).resize((avatar_size[0] // 2, avatar_size[1] // 2))

        new_img_width = author_image.width + user_image.width
        new_img_height = max(author_image.height, user_image.height, love_img.height)
        new_img = Image.new('RGB', (new_img_width, new_img_height))
        new_img.paste(author_image, (0, (new_img_height - author_image.height) // 2))
        new_img.paste(user_image, (author_image.width, (new_img_height - user_image.height) // 2))
        new_img.paste(
            love_img,
            (
                (new_img_width - love_img.width) // 2,
                (new_img_height - love_img.height) // 2
            ),
            mask=love_img,
        )

        with io.BytesIO() as buffer:
            new_img.save(buffer, format='PNG')
            buffer.seek(0)
            discord_file = discord.File(fp=buffer, filename='love.png')

        embed = discord.Embed(title=f"Love Percentage: {love_percentage}%", color=0xFF69B4)
        embed.set_image(url="attachment://love.png")
        embed.set_footer(text=f"Love from {interaction.user.display_name} to {user.display_name}")
        await interaction.response.send_message(file=discord_file, embed=embed)

    async def fetch_image(self, url):
        with self.bot.http_session as session:
            with session.get(url) as resp:
                return resp.content

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Love(bot))
