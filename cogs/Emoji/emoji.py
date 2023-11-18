import discord
from discord.ext import commands
from discord import app_commands
from discord.errors import HTTPException
import aiohttp
import re
import random

class EmojiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.session = aiohttp.ClientSession()

    @app_commands.command(name="steal", description="Steal an emoji and add it to your server")
    @discord.app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def steal(self, ctx, name: str, emoji: str):
        # Extract emoji ID from the string
        match = re.search(r'<a?:\w+:(\d+)>', emoji)
        if not match:
            await ctx.response.send_message("Invalid emoji format.")
            return

        emoji_id = match.group(1)
        is_animated = emoji.startswith('<a:')  # Detect animation
        file_extension = 'gif' if is_animated else 'png'  # Set the file extension
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_extension}"  # Update URL

        async with self.bot.session.get(emoji_url) as resp:
            if resp.status != 200:
                await ctx.response.send_message("Failed to download emoji.")
                return
            image_data = await resp.read()

        try:
            new_emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
            await ctx.response.send_message(f"Emoji {new_emoji} added to the server with the name {name}.")
        except HTTPException as e:
            await ctx.response.send_message(f"Failed to add emoji: {e.text}")

    @steal.error 
    async def steal_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")


    @app_commands.command(name="bigemoji", description="Show a bigger version of an emoji")
    async def bigemoji(self, ctx, emoji: str):
        # Extract emoji ID from the string
        match = re.search(r'<a?:\w+:(\d+)>', emoji)
        if not match:
            await ctx.response.send_message("Invalid emoji format.")
            return

        emoji_id = match.group(1)
        is_animated = emoji.startswith('<a:')
        
        png_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        jpg_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.jpg"
        gif_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif" if is_animated else None
        
        # Generate a random color for the embed
        random_color = random.randint(0, 0xFFFFFF)

        embed = discord.Embed(color=random_color)
        embed.set_image(url=png_url)
        
        download_links = f"[PNG]({png_url}) | [JPG]({jpg_url})"
        if gif_url:
            download_links += f" | [GIF]({gif_url})"
        
        embed.add_field(name="Download", value=download_links)
        embed.set_footer(text=f"Emoji ID: {emoji_id}")
        await ctx.response.send_message(embed=embed)

    @steal.error 
    async def steal_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")


def setup(bot):
    bot.add_cog(EmojiCog(bot))
