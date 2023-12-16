import datetime

from discord import app_commands, Embed, Interaction, Color, Message
from discord.ext import commands

from bot import EGirlzStoreBot


class Snipe(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self._last_deleted_message = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        # Ignore direct messages
        if message.guild is None:
            return
        # Store a tuple containing the message content, author, and time of deletion
        self._last_deleted_message[message.channel.id] = (
            message.content,
            message.author,
            datetime.datetime.utcnow(),
        )

    @app_commands.command(
        name="snipe",
        description="Retrieve the last deleted message in the channel."
    )
    async def snipe(self, interaction: Interaction):
        channel_id = interaction.channel_id
        if channel_id in self._last_deleted_message:
            content, author, time_of_deletion = self._last_deleted_message[channel_id]
            embed = Embed(description=content, color=Color.red(), timestamp=time_of_deletion)
            embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
            embed.set_footer(text=f"Message deleted")
            # Clear the snipe after showing it
            del self._last_deleted_message[channel_id]
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No message to snipe!", ephemeral=True)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Snipe(bot))
