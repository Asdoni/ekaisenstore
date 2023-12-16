from random import randint

from discord import app_commands, Embed
from discord.ext import commands

from bot import EGirlzStoreBot


class PP(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="pp",
        description="Measure your PP"
    )
    async def peepee(self, ctx):
        special_user = ctx.user.id == 209748857683312640
        # 1/20 chance not finding any pp :,(
        if not randint(0, 19) and not special_user:
            description = (
                f"<:smolPP:1062443373165822022> I'm sorry {ctx.user.mention},"
                f" PP not found <:smolPP:1062443373165822022>"
            )
            title = f"{ctx.user.display_name}'s PP"
        else:
            if special_user:
                pp_length = 30
            else:
                # 1/100 chance to set massive pp else random length between 1 and 30
                pp_length = randint(1, 30) if randint(0, 99) else 100
            description = f"8{'=' * pp_length}>"
            title = f"{ctx.user.display_name}'s PP is {pp_length} CM"
        embed = Embed(
            title=title,
            description=description,
            color=randint(0, 0xFFFFFF)
        )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(PP(bot))
