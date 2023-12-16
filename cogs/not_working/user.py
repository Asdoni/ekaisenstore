import json
import re
import time

import DiscordUtils
import discord
from discord.ext import commands, flags
from discord.ext.commands import MissingRequiredArgument

from bot import EGirlzStoreBot
from cogs.MyAnimeList.myanimelist import userstatus

"""To get the lists of animes/mangas and send them in the form of an embed."""


async def status(ctx, userlist, title):
    status_list = []
    for i in range(0, len(userlist)):
        status_list.append('**' + str(i + 1) + '.** ' + userlist[i]['title'])
    stat = '\n'.join(status_list)
    embed = discord.Embed(title=title, color=0x70ff72, description=stat)
    await ctx.send(embed=embed)


"""To get the lists of animes/mangas and send them in the form of multiple embeds when length > 15."""


async def bigstatus(ctx, userlist, title):
    status_list = []
    for i in range(0, len(userlist)):
        status_list.append('**' + str(i + 1) + '.** ' + userlist[i]['title'])
    L = status_list
    n = 15
    new_list = [L[x: x + n] for x in range(0, len(L), n)]
    embed_list = []
    list_len = len(new_list)
    for i in range(0, len(new_list)):
        stat = '\n'.join(new_list[i])
        embed = discord.Embed(title=title, color=0x70ff72, description=stat)
        embed.set_footer(text=f'{i + 1} / {list_len}')
        embed_list.append(embed)
    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('🔐', "lock")
    await paginator.run(embed_list)


"""To remove the html tags from the about page and return string."""


def htmltag(text, username):
    if text:
        return re.sub(re.compile('<.*?>'), '', text)
    return f'This is the profile of {username["username"]}.'


"""To get the lists of favorites of user."""


def favorites(category, username, embed):
    fav_list = []
    for i in range(0, len(username['favorites'][category])):
        fav_list.append(username['favorites'][category][i]['name'])
    if len(fav_list) > 0:
        category = category.title()
        return embed.add_field(name=f'__Favorite {category}__', value='\n'.join(fav_list), inline=False)
    else:
        category = category.title()
        return embed.add_field(name=f'__Favorite {category}__', value=f'No favorite {category} yet. ', inline=False)


# Load the bot configuration
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    prefix = config_data['prefix']

mal_name = 'wildcyclotron'
help_command = (
    f'`{prefix}user {mal_name}`\n`{prefix}user {mal_name} --watching`\n`{prefix}u {mal_name}'
    f' --completed `\n`{prefix}u {mal_name} --onhold`\n`{prefix}u {mal_name} --ptw`\n`{prefix}u'
    f' {mal_name} --dropped`\n`{prefix}u {mal_name} --completed --m`\n`{prefix}u {mal_name}'
    f' --dropped --m`\n`{prefix}u {mal_name} --onhold --m`\n`{prefix}u {mal_name}'
    f' --reading`\n`{prefix}u {mal_name} --ptr`'
)

desc = (
    f"Shows detailed information about MyAnimeList user's list or sends you the general profile"
    f" information about their profile.\n \n Use flag `--m` or `--manga` to specify if you need manga"
    f" list of a particular flag. \n \n For example, if you want to look into completed manga(s) of"
    f" user {mal_name}: `{prefix}user {mal_name} --completed --m` \n \n For flags like `--reading` or"
    f" `--ptr`(or `--plantoread`), you may or may not specify the `--manga` flag because it's obvious"
    f" that they belong to manga list. \n \n **Note:** The position of flags doesn't matter i.e"
    f" `--dropped --m` is same as `--m --dropped`."
)


class User_Info(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @flags.add_flag("--watching", action="store_true")
    @flags.add_flag("--ptw", '--plantowatch', action="store_true")
    @flags.add_flag("--onhold", action="store_true")
    @flags.add_flag("--dropped", action="store_true")
    @flags.add_flag("--completed", action="store_true")
    @flags.add_flag("--ptr", '--plantoread', action="store_true")
    @flags.add_flag("--reading", '--r', action="store_true")
    @flags.add_flag("--m", "--manga", action="store_true")
    @flags.command(name='user', aliases=['u'], brief='Get information about an user.', description=desc,
                   usage=f'`{prefix}user <name> [--manga] [--reading] [--ptr] [--completed] [--dropped] [--onhold] [--ptw] [--watching]`',
                   help=help_command)
    async def user(self, ctx, name, **flags):

        if ctx.guild:
            pass
        else:
            return

        try:
            url = f'https://api.jikan.moe/v3/user/{name}'
            username = self.bot.http_session.get(url).json() # jikanjson(url)
        except:
            await ctx.send('No such user found.')
            return

        msg = await ctx.send('Searching for your query, please wait. <a:bot_loading:869160757546340394>')
        time.sleep(3)
        await msg.delete()

        """Sends different outputs depending on the flags passed. I don't know if this is the best way to do it."""

        if flags['watching']:
            url = f'https://api.jikan.moe/v3/user/{name}/animelist/watching'
            await userstatus(self, ctx, name, url, status, bigstatus, 'anime', 'Watching')

        elif flags['ptw']:
            url = f'https://api.jikan.moe/v3/user/{name}/animelist/ptw'
            await userstatus(self, ctx, name, url, status, bigstatus, 'anime', 'Plan to Watch')

        elif flags['onhold'] and flags['m']:
            url = f'https://api.jikan.moe/v3/user/{name}/mangalist/onhold'
            await userstatus(self,ctx, name, url, status, bigstatus, 'manga', 'On Hold (Manga)')

        elif flags['onhold']:
            url = f'https://api.jikan.moe/v3/user/{name}/animelist/onhold'
            await userstatus(self,ctx, name, url, status, bigstatus, 'anime', 'On Hold (Anime)')

        elif flags['dropped'] and flags['m']:
            url = f'https://api.jikan.moe/v3/user/{name}/mangalist/dropped'
            await userstatus(self,ctx, name, url, status, bigstatus, 'manga', 'Dropped (Manga)')

        elif flags['dropped']:
            url = f'https://api.jikan.moe/v3/user/{name}/animelist/dropped'
            await userstatus(self,ctx, name, url, status, bigstatus, 'anime', 'Dropped (Anime)')

        elif flags['completed'] and flags['m']:
            url = f'https://api.jikan.moe/v3/user/{name}/mangalist/completed'
            await userstatus(self,ctx, name, url, status, bigstatus, 'manga', 'Completed (Manga)')

        elif flags['completed']:
            url = f'https://api.jikan.moe/v3/user/{name}/animelist/completed'
            await userstatus(self,ctx, name, url, status, bigstatus, 'anime', 'Completed (Anime)')

        elif flags['reading']:
            url = f'https://api.jikan.moe/v3/user/{name}/mangalist/reading'
            await userstatus(self,ctx, name, url, status, bigstatus, 'manga', 'Reading')

        elif flags['ptr']:
            url = f'https://api.jikan.moe/v3/user/{name}/mangalist/ptr'
            await userstatus(self,ctx, name, url, status, bigstatus, 'manga', 'Plan to Read')

        else:
            embed = discord.Embed(
                title=username['username'], url=username['url'],
                description=htmltag(username['about'], username), color=0x70ff72
            )
            if username['image_url']:
                embed.set_thumbnail(url=username['image_url'])
            else:
                embed.set_thumbnail(
                    url='https://media.discordapp.net/attachments/870414758006911036/871216478324678656/unknown.png')

            favorites('anime', username, embed)
            favorites('manga', username, embed)
            favorites('characters', username, embed)
            favorites('people', username, embed)
            await ctx.send(embed=embed)

    @user.error
    async def user_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            if ctx.guild:
                await ctx.send('Please provide a username.')
            else:
                return


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(User_Info(bot))
