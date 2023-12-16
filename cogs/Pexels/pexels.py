import os
import random

from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot

pixelskey = os.environ.get('PIXELS_KEY')


class Pexels(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name='bunny',
        description='Get a random bunny picture',
    )
    async def bunny(self, ctx):
        headers = {'Authorization': pixelskey}
        with self.bot.http_session as session:
            with session.get('https://api.pexels.com/v1/search?query=bunny', headers=headers) as response:
                data = response.json()
        random_pic = random.choice(data['photos'])['src']['medium']
        await ctx.response.send_message(random_pic)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Pexels(bot))
