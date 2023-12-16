import discord
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot


class Echo(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="echo",
        description="Echoes what you say."
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def echo(self, interaction: discord.Interaction, message: str, channel: discord.abc.GuildChannel = None):
        target_channel = channel or interaction.channel
        await target_channel.send(message)
        await interaction.response.send_message(f"Message sent to {target_channel.mention}", ephemeral=True)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Echo(bot))
