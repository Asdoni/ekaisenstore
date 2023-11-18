# Imports the required modules and packages.
import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import MissingRequiredArgument
import DiscordUtils
import json
from cogs.MyAnimeList.getjson import jikanjson
from cogs.MyAnimeList.getname import getname
from cogs.MyAnimeList.results import results
from cogs.MyAnimeList.selection import selection
import os

# Reads the bot's prefix from a config file.
prefix = os.environ.get('PREFIX')

# Defines the Character_Info class, inheriting from commands.Cog.
class Character_Info(commands.Cog):
  def __init__(self, client):
    self.client = client

  # Defines the command's metadata
  desc = 'Gives information about a character via '+ '[MyAnimeList](https://myanimelist.net/).'
  help_command = f'`{prefix}character Mikasa Ackerman`\n`{prefix}char Oreki Houtarou`\n`{prefix}char リヴァイ`'

  # Defines the 'character' command
  @commands.command(name='character',no_pm=True,aliases=['char'],brief = 'Get Information about a character from an anime or manga.',usage=f'`{prefix}character <name>`\n`{prefix}char <name>`',description=desc,help=help_command)
  async def character(self,ctx,*,name):
    # Deletes the user's command message
    await ctx.message.delete()

    # Checks if the command was invoked in a guild
    if ctx.guild:
      pass
    else:
      return
    
    # Gets the formatted name for API request
    query = getname(name)
    # URL for the API request
    url = f'https://api.jikan.moe/v4/characters?q={query}&order_by=favorites&sort=desc&page=1'
    search_result = jikanjson(url)
    data = search_result['data']
    data_len = len(search_result['data'])
    # If no results, exits early
    if data_len == 0:
      await ctx.send('No results for query.')
      return
    elif data_len == 1:
      n = 0
    else:
      # Calls for additional functions to narrow down selection.
      output = results(data,'name',name,'characters')
      output_message = await ctx.send(output)
      selection_result = await selection(self,ctx,output_message,data_len,'character')
      if selection_result:
        n = selection_result - 1
      else:
        return 

    search = search_result['data'][n]
    char_about = search['about']

    if len(char_about)>4000:
      message = await ctx.send('Too much information about this character. Slicing the info till 4000 words <a:bot_loading:869160757546340394> ')
      char_about= char_about[:3900]
      await asyncio.sleep(6)
      embed=discord.Embed(title=search['name'], url=search["url"] , description=char_about+'...', color=0x8a7bff)
      embed.add_field(name='Member Favorites',value=search['favorites'], inline= False)
      embed.set_image(url=search['images']['jpg']['image_url'])
      await message.delete()
      await ctx.send(embed=embed)
    else:
      char_about = char_about
      embed=discord.Embed(title=search['name'], url=search["url"] , description=char_about, color=0x8e37b0)
      embed.add_field(name='Member Favorites',value=search['favorites'], inline= False)
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
  desc = 'Fetch images for a particular character from anime or manga via '+ '[MyAnimeList](https://myanimelist.net/).'

  # Defines the 'images' command
  @commands.command(name='images', no_pm=True, aliases=['im', 'image'], brief='Get images for a character from an anime or manga.', usage=f'{prefix}images <name>', description=desc, help=help_command)
  async def images(self, ctx, *, name):
      # Deletes the user's command message
      await ctx.message.delete()

      # Initialize pic_list and embed_list here
      pic_list = []
      embed_list = []

      # Checks if the command was invoked in a guild
      if ctx.guild:
          pass
      else:
          return
      
      if name == 'your mom':
          await ctx.send('https://pbs.twimg.com/media/EUOBhctUEAAWWJj.jpg')
          return

      # Gets the formatted name for API request
      query = getname(name)
      # URL for the API request
      url = f'https://api.jikan.moe/v4/characters?q={query}&order_by=favorites&sort=desc&page=1'
      search_result = jikanjson(url)
      data = search_result['data']
      data_len = len(search_result['data'])
      # If no results, exits early
      if data_len == 1:
          n = 0
      elif data_len == 0:
          await ctx.send('No results for query.')
          return
      else:
          # Calls for additional functions to narrow down selection.
          output = results(data, 'name', name, 'characters')
          output_message = await ctx.send(output)
          selection_result = await selection(self, ctx, output_message, data_len, 'character')
          if selection_result:
              n = selection_result - 1
          else:
              return

      search = search_result['data'][n]
      characterid = search['mal_id']
      char_pictures = jikanjson(f'https://api.jikan.moe/v4/characters/{characterid}/pictures')
      pic_len = len(char_pictures['data'])
      
      if pic_len == 0:
          await ctx.send(f'Zero pictures available for this character.')
          return
      else:
          pass

      pic_list = []
      for entry in char_pictures['data']:
          image_url = entry.get('jpg', {}).get('image_url')
          if image_url:
              pic_list.append(image_url)

      len_half = int(len(pic_list) / 2)

      pictures_list = pic_list[0:len_half]
      pictures_len = len(pictures_list)
      embed_list = []

      for i in range(0, len(pictures_list)):
          embed1 = discord.Embed(title=search['name'], color=0x8a7bff, description='__Favorites__ : ' + str(search['favorites']))
          embed1.set_image(url=pic_list[i])
          embed1.set_footer(text=f'{i + 1} / {pictures_len}')
          embed_list.append(embed1)

      paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
      paginator.add_reaction('⏪', "back")
      paginator.add_reaction('⏩', "next")
      paginator.add_reaction('🔐', "lock")

      # Populate embed_list
      pictures_list = pic_list[0:len_half]
      pictures_len = len(pictures_list)
      for i in range(0, len(pictures_list)):
          embed1 = discord.Embed(title=search['name'], color=0x8a7bff, description='__Favorites__ : ' + str(search['favorites']))
          embed1.set_image(url=pic_list[i])
          embed1.set_footer(text=f'{i + 1} / {pictures_len}')
          embed_list.append(embed1)

      try:
        await paginator.run(embed_list)
      except Exception as e:
        await ctx.send(f"Here is the first image of {search['name']}:", embed=embed_list[0])
        

  async def cog_command_error(self, ctx, error):
    # Generic error handling for the Cog
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(f"Command failed due to an internal error: {error.original}")
    else:
        await ctx.send(f"An error occurred: {error}")

  @images.error
  async def image_error(self,ctx,error):
    # Error handling for the 'images' command
    if isinstance(error,(MissingRequiredArgument)):
      if ctx.guild:
        await ctx.send('Please provide a query.')
      else:
        return
  
# Function to add the Cog to the bot
def setup(bot):
  bot.add_cog(Character_Info(bot))
