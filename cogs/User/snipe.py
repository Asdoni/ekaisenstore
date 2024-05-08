import datetime
import discord
from discord import app_commands, Embed, Color
from discord.ext import commands

from bot import EGirlzStoreBot

class Snipe(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self._last_deleted_message = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None and message.author != self.bot.user:
            return

        self._last_deleted_message[message.channel.id] = (
            message.content,
            message.author.display_name,
            message.author.display_avatar.url,
            datetime.datetime.utcnow()
        )

    @app_commands.command(
        name="snipe",
        description="Retrieve the last deleted message in the channel."
    )
    async def snipe(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id in self._last_deleted_message:
            content, author_name, author_avatar, time_of_deletion = self._last_deleted_message[channel_id]
            
            embed = Embed(description=content, color=Color.red(), timestamp=time_of_deletion)
            embed.set_author(name=author_name, icon_url=author_avatar)
            embed.set_footer(text=f"Message deleted")

            await interaction.response.send_message(embed=embed)
            
            del self._last_deleted_message[channel_id]
        else:
            await interaction.response.send_message("No message to snipe!", ephemeral=True)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Snipe(bot))