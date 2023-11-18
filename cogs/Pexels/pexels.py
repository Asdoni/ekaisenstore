from discord.ext import commands
from discord import app_commands
import aiohttp
import random
import os

pixelskey = os.environ.get('PIXELS_KEY')

class Pexels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='bunny',
        description='Get a random bunny picture',
    )
    async def bunny(self, ctx):
        headers = {'Authorization': pixelskey}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.pexels.com/v1/search?query=bunny', headers=headers) as response:
                data = await response.json()
        random_pic = random.choice(data['photos'])['src']['medium']
        await ctx.response.send_message(random_pic)

def setup(bot):
    bot.add_cog(Pexels(bot))
