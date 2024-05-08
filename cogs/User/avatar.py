import random

import discord
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot


class AvatarCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="avatar",
        description="Get the avatar of a user"
    )
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        if not user:
            user = interaction.user

        random_color = random.randint(0, 0xFFFFFF)
        png_url = user.display_avatar.replace(format="png").url
        jpg_url = user.display_avatar.replace(format="jpg").url
        gif_url = user.display_avatar.replace(format="gif").url if user.display_avatar.is_animated() else None

        embed = discord.Embed(title=f"{user.name}'s Avatar", color=random_color)
        embed.set_image(url=user.display_avatar.url)
        download_links = f"[PNG]({png_url}) | [JPG]({jpg_url})"
        if gif_url:
            download_links += f" | [GIF]({gif_url})"
        embed.add_field(name="Download", value=download_links)
        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(AvatarCog(bot))
