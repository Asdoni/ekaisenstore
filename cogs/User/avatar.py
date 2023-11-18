import discord
from discord.ext import commands
from discord import app_commands
import random

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="avatar",
        description="Get the avatar of a user"
    )
    async def avatar(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.user

        # Generating a random color for the embed.
        random_color = random.randint(0, 0xFFFFFF)

        # Avatar URL for PNG, JPG, and GIF.
        png_url = user.display_avatar.replace(format="png").url
        jpg_url = user.display_avatar.replace(format="jpg").url
        gif_url = user.display_avatar.replace(format="gif").url if user.display_avatar.is_animated() else None

        embed = discord.Embed(title=f"{user.name}'s Avatar", color=random_color)
        embed.set_image(url=user.display_avatar.url)
        download_links = f"[PNG]({png_url}) | [JPG]({jpg_url})"
        if gif_url:  # Only add the GIF link if the avatar is animated.
            download_links += f" | [GIF]({gif_url})"
        embed.add_field(name="Download", value=download_links)
        await ctx.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(AvatarCog(bot))
