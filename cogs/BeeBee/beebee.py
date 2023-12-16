import random
from discord import app_commands, Embed
from discord.ext import commands

from bot import EGirlzStoreBot

def get_booby_line(size: int, amount=2) -> str:
    spaces = ' \u200B' * size
    return f'({spaces}.{spaces})' * amount

class BB(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="bb",
        description="Measure your boobies"
    )
    async def boobies(self, ctx):
        random_color = random.randint(0, 0xFFFFFF)
        bb_not_found = False
        triple_boob = False

        if ctx.user.id == 209748857683312640:
            random_size = 9
        else:
            if random.randint(1, 100) <= 3.5:
                bb_not_found = True
            triple_boob = not random.randint(0, 99)
            random_size = random.randint(0, 9)

        if bb_not_found:
            embed = Embed(
                title=f"{ctx.user.display_name}'s bb",
                description=(
                    f"<:smolpp:1062443373165822022> I'm sorry {ctx.user.mention}, you are flat!"
                    f" <:smolpp:1062443373165822022>"
                ),
                color=random_color,
            )
        elif triple_boob:
            embed = Embed(
                title=f"{ctx.user.display_name}'s boobies are special!",
                description=get_booby_line(4, 3),
                color=random_color,
            )
        else:
            cup_sizes = "ABCDEFGHI"
            cup_size = 'AA' if not random_size else cup_sizes[random_size - 1:random_size]
            embed = Embed(
                title=f"{ctx.user.display_name}'s boobies are {cup_size} cup!",
                description=get_booby_line(random_size * 2),
                color=random_color,
            )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(BB(bot))
