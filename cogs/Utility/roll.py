import random

from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands

from bot import EGirlzStoreBot

class RollCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="roll",
        description="Roll the dice")
    async def roll(self, interaction: Interaction):
        random_number = random.randint(1, 100)

        emotes = {
            (1, 10): "<:andoni:1156911271019552840>",
            (11, 20): "<:pepePoint:1156906733034295296>",
            (21, 40): "<:xorinoob:1156912140574277714>",
            (41, 89): "<:ok:1156913055494586428>",
            (90, 99): "<:POGGERS:1156906925498310766>",
            (100, 100): "<a:Peepo_Hacker:1156907116775342131>",
        }

        emote = next(
            (emote for (min_range, max_range), emote in emotes.items() if min_range <= random_number <= max_range),
            "",
        )

        embed = Embed(
            title="🎲 Roll the Dice 🎲",
            description=f"{emote}  You rolled a {random_number}!  {emote}",
            color=Color.random()
        )

        author_name = interaction.user.display_name
        author_avatar_url = interaction.user.display_avatar.url
        embed.set_author(name=author_name, icon_url=author_avatar_url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(RollCog(bot))
