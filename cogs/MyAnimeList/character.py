# Imports the required modules and packages.
import os

import DiscordUtils
import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument

from bot import EGirlzStoreBot
from cogs.MyAnimeList.myanimelist import results, selection

# Reads the bot's prefix from a config file.
prefix = os.environ.get('PREFIX')


# Defines the Character_Info class, inheriting from commands.Cog.
class CharacterInfo(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    # Defines the command's metadata
    desc = 'Gives information about a character via ' + '[MyAnimeList](https://myanimelist.net/).'
    help_command = f'`{prefix}character Mikasa Ackerman`\n`{prefix}char Oreki Houtarou`\n`{prefix}char リヴァイ`'

    # Defines the 'character' command
    @commands.command(name='character', no_pm=True, aliases=['char'],
                      brief='Get Information about a character from an anime or manga.',
                      usage=f'`{prefix}character <name>`\n`{prefix}char <name>`', description=desc, help=help_command)
    async def character(self, ctx, *, name:str):
        # Deletes the user's command message
        await ctx.message.delete()

        # Checks if the command was invoked in a guild
        if ctx.guild:
            pass
        else:
            return

        # Gets the formatted name for API request
        query = '%20'.join(name.split(' '))
        # URL for the API request
        url = f'https://api.jikan.moe/v4/characters?q={query}&order_by=favorites&sort=desc&page=1'
        search_result = self.bot.http_session.get(url).json()  # jikanjson(url)
        data = search_result['data']
        data_len = len(search_result['data'])
        # If no results, exits early
        if not data_len:
            return await ctx.send('No results for query.')
        elif data_len == 1:
            n = 0
        else:
            # Calls for additional functions to narrow down selection.
            output = results(data, 'name', name, 'characters')
            output_message = await ctx.send(output)
            selection_result = await selection(self, ctx, output_message, data_len, 'character')
            if not selection_result:
                return
            n = selection_result - 1

        search = data[n]
        char_about = search['about']
        description_limit = 4000
        if len(char_about) > description_limit:
            # split up description and build multiple embeds
            descriptions = [char_about[i:i + description_limit] for i in range(0, len(char_about), description_limit)]
            embeds = []
            for i in range(len(descriptions)):
                embed = discord.Embed(
                    title=search['name'],
                    url=search["url"],
                    description=descriptions[i],
                    color=0x8a7bff,
                )
                if not i:
                    embed.add_field(name='Member Favorites', value=search['favorites'], inline=False)
                    embed.set_image(url=search['images']['jpg']['image_url'])
                embed.set_footer(text=f'{i + 1} / {len(descriptions)}')
                embeds.append(embed)
            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True, timeout=-1)
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")
            await paginator.run(embeds)
        else:
            embed = discord.Embed(title=search['name'], url=search["url"], description=char_about, color=0x8e37b0)
            embed.add_field(name='Member Favorites', value=search['favorites'], inline=False)
            embed.set_image(url=search['images']['jpg']['image_url'])
            await ctx.send(embed=embed)

    @character.error
    async def char_error(self, ctx, error):
        # Error handling for the 'character' command
        if isinstance(error, MissingRequiredArgument) and ctx.guild:
            await ctx.send('Please provide a query.')
        if ctx.guild:
            await ctx.send('Please provide a query.')
        else:
            return

    # Defines the command's metadata
    help_command = f'`{prefix}images Mikasa Ackerman`\n`{prefix}image Lelouch`\n`{prefix}im Eru Chitanda `\n`{prefix}im Midoriya Izuku`\n~~`{prefix}im your mom`~~'
    desc = 'Fetch images for a particular character from anime or manga via ' + '[MyAnimeList](https://myanimelist.net/).'

    # Defines the 'images' command
    @commands.command(name='images', no_pm=True, aliases=['im', 'image'],
                      brief='Get images for a character from an anime or manga.', usage=f'{prefix}images <name>',
                      description=desc, help=help_command)
    async def images(self, ctx, *, name:str):
        # Deletes the user's command message
        await ctx.message.delete()

        # Checks if the command was invoked in a guild
        if not ctx.guild:
            return

        if name == 'your mom':
            return await ctx.send('https://pbs.twimg.com/media/EUOBhctUEAAWWJj.jpg')


        # Gets the formatted name for API request
        query = '%20'.join(name.split(' '))
        # URL for the API request
        url = f'https://api.jikan.moe/v4/characters?q={query}&order_by=favorites&sort=desc&page=1'
        search_result = self.bot.http_session.get(url).json()  # jikanjson()
        char_data = search_result['data']
        # If no results, exits early
        if not char_data:
            return await ctx.send('No results for query.')

        # if only one result
        elif len(char_data) == 1:
            char_idx = 0
        else:
            # Calls for additional functions to narrow down selection.
            output = results(char_data, 'name', name, 'characters')
            output_message = await ctx.send(output)
            selection_result = await selection(self, ctx, output_message, len(char_data), 'character')
            if not selection_result:
                return
            char_idx = selection_result - 1
        search = char_data[char_idx]
        url = f"https://api.jikan.moe/v4/characters/{search['mal_id']}/pictures"
        char_pictures = self.bot.http_session.get(url).json()  # jikanjson(url)
        pic_data = char_pictures["data"]
        if not pic_data:
            await ctx.send(f'Zero pictures available for this character.')
            return
        pic_list = []
        for entry in pic_data:
            image_url = entry.get('jpg', {}).get('image_url')
            if image_url:
                pic_list.append(image_url)
        embed_list = []
        for i in range(len(pic_list)):
            embed = discord.Embed(
                title=search['name'],
                color=0x8a7bff,
                description='__Favorites__ : ' + str(search['favorites']),
            )
            embed.set_image(url=pic_list[i])
            embed.set_footer(text=f'{i + 1} / {len(pic_list)}')
            embed_list.append(embed)
        if embed_list:
            if len(embed_list) == 1:
                await ctx.send(embed=embed_list[0])
            else:
                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏪', "back")
                paginator.add_reaction('⏩', "next")
                paginator.add_reaction('🔐', "lock")
                await paginator.run(embed_list)

    async def cog_command_error(self, ctx, error):
        # Generic error handling for the Cog
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"Command failed due to an internal error: {error.original}")
        else:
            await ctx.send(f"An error occurred: {error}")

    @images.error
    async def image_error(self, ctx, error):
        # Error handling for the 'images' command
        if isinstance(error, MissingRequiredArgument):
            if ctx.guild:
                await ctx.send('Please provide a query.')
            else:
                return


# Function to add the Cog to the bot
async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(CharacterInfo(bot))
