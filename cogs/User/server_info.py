import discord
from discord import app_commands
from discord.ext import commands
import calendar

from bot import EGirlzStoreBot

class ServerInfoCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="server_info",
        description="Get information about the server"
    )
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.")
            return

        random_color = discord.Colour.random()

        icon_url = None
        download_links = "No server icon available."

        if guild.icon:
            png_url = guild.icon.replace(format="png").url
            jpg_url = guild.icon.replace(format="jpg").url
            gif_url = guild.icon.replace(format="gif").url if guild.icon.is_animated() else None
            icon_url = guild.icon.url

            download_links = f"[PNG]({png_url}) | [JPG]({jpg_url})"
            if gif_url:
                download_links += f" | [GIF]({gif_url})"

        created_timestamp = calendar.timegm(guild.created_at.utctimetuple())

        embed = discord.Embed(title=f"Information about {guild.name}", color=random_color)
        if icon_url:
            embed.set_thumbnail(url=icon_url)
        embed.add_field(name="Member Count", value=str(guild.member_count), inline=False)
        embed.add_field(name="Owner", value=str(guild.owner.mention), inline=False)
        embed.add_field(
            name="Creation Date",
            value=f"<t:{created_timestamp}:F> (<t:{created_timestamp}:R>)",
            inline=False
        )
        embed.add_field(name="Server ID", value=str(guild.id), inline=False)
        embed.add_field(name="Download Server Icon", value=download_links, inline=False)

        if icon_url:
            embed.set_footer(text=f"Server Info - {guild.name}", icon_url=icon_url)
        else:
            embed.set_footer(text=f"Server Info - {guild.name}")

        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(ServerInfoCog(bot))