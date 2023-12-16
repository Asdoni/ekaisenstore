import asyncio

import discord
from discord.ext import commands

from bot import EGirlzStoreBot


class MyAnimeList(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @commands.command(name='malcmd', aliases=['helpc', 'hcom'],
                      brief='Show a list of available commands for MyAnimeList.',
                      description='Shows a list of all available commands and their usage.')
    async def my_anime_list_help_cmd(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="MyAnimeList Command List:", color=0x8a7bff)
        embed.add_field(
            name="Character Info:",
            value=(
                "Get information about a character from an anime or manga.\n"
                "Usage: `$character <name>` or `$char <name>`\n"
                "Example: `$character Mikasa Ackerman` or `$char Oreki Houtarou`"
            ),
            inline=False,
        )
        embed.add_field(
            name="Character Images:",
            value=(
                "Fetch images for a character from an anime or manga.\n"
                "Usage: `$images <name>`, `$image <name>`, or `$im <name>`\n"
                "Example: `$images Mikasa Ackerman`, `$image Lelouch`, or `$im Eru Chitanda`"
            ),
            inline=False,
        )
        embed.add_field(
            name="Anime Info:",
            value=(
                "Get information about an anime.\n"
                "Usage: `$anime <name>`\n"
                "Example: `$anime Hyouka`, `$anime NHK ni Youkoso!`"
            ),
            inline=False,
        )
        embed.add_field(
            name="Manga Info:",
            value=(
                "Get information about a manga.\n"
                "Usage: `$manga <name>`\n"
                "Example: `$manga Omniscient Reader`, `$manga attack on titan`"
            ),
            inline=False,
        )
        embed.set_footer(text="Note: Some commands have aliases for shorter usage.")
        await ctx.send(embed=embed)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(MyAnimeList(bot))


def results(data, name, query, type_):
    result_list = [f'{str(n + 1)}.   {data[n][name]}' for n in range(0, len(data))]
    pre_message = f'`{len(data)}` {type_} found matching `{query}`!'
    post_message = 'Please type the number corresponding to your selection, or type `c` now to cancel.'

    message = '\n '.join(result_list)
    output = f'{pre_message}\n \n```md\n {message}\n```\n {post_message}'
    return output


async def selection(self, ctx, message, data_len, type_):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while True:
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Sorry, you didn't reply in time!")
            return None

        if msg.content.isdigit():
            if int(msg.content) in [*range(1, data_len + 1)]:
                await message.delete()
                await msg.delete()
                return int(msg.content)
            else:
                continue
        elif msg.content.lower() == 'c':
            await message.delete()
            await msg.delete()
            await ctx.send(f'{ctx.author.name} cancelled the {type_} selection.')
            return None
        else:
            continue


async def userstatus(self, ctx, name, url, status, bigstatus, type_, title):
    try:
        user_status = self.bot.http_session.get(url).json()  # jikanjson(url)
    except:
        await ctx.send(f"{name}'s list is not public :smiling_face_with_tear: ")
        return
    user_list = user_status[type_]
    if len(user_list) > 15:
        await bigstatus(ctx, user_list, title)
    elif len(user_list) == 0:
        await ctx.send(f'Nothing found in their {title} list.')
    else:
        await status(ctx, user_list, title)
