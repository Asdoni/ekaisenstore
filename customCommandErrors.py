from typing import Optional

from discord import Interaction, Member
from discord.app_commands import CheckFailure

"""
HOW TO USE

Example:

class ExampleCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
    
    @app_commands.command(name="example", description="Example command")
    @app_commands.check(is_channel_nsfw)    # import check from this file
    async def example(self, interaction:Interaction):
        await ctx.response.send_message("This command worked because the channel is nswf")
        
"""


def is_channel_nsfw(interaction: Interaction) -> bool:
    if not interaction.channel.is_nsfw():
        raise NSWFError()
    return True

class NSWFError(CheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or 'This command can only be used in a nsfw channel.')


class TranslationError(Exception):
    def __init__(self, message):
        super().__init__(message or "Failed to translate message.")

        

# add more custom errors and checks if needed
