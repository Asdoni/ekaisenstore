import discord
from discord import app_commands
from discord.ext import commands
from discord import User

from bot import EGirlzStoreBot

class DirectMessage(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="dmuser",
        description="Sends a DM to a user."
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def dmuser(self, interaction: discord.Interaction, user: User, message: str):
        await interaction.response.defer(ephemeral=True)

        if user.dm_channel is None:
            await user.create_dm()
        try:
            await user.dm_channel.send(message)
            await interaction.followup.send(f"Message sent to {user.mention}", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"Failed to send message to {user.mention}: {e}", ephemeral=True)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(DirectMessage(bot))
