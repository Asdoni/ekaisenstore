import os
import sys
import logging
import json
import platform
from discord import app_commands
from colorama import Fore
from datetime import datetime
import discord
from discord.ext import commands
from bot import bot
from cogs.Dingo.dingo import Dingo
from cogs.Welcome.welcome import Welcome
from cogs.Throw.throw import Throw
from cogs.User.info import InfoCog
from cogs.ChatGPT.chatgpt import ChatGPT
from cogs.Translator.translator import TranslatorCog
#from cogs.Kiwi_Game.kiwi import Kiwi
from cogs.User.avatar import AvatarCog
from cogs.Horny.horny import HornyCog
#from cogs.Loot_Tracker.loot import SheetsCog
from cogs.PeePee.peepee import PP
from cogs.Trivia.trivia import Trivia
from cogs.Love.love import Love
#from cogs.Javir.javir import Javir
from cogs.MyAnimeList.character import Character_Info
#from cogs.MyAnimeList.myanimelist import MyAnimeList
from cogs.MyAnimeList.userflags import userstatus
from cogs.MyAnimeList.getjson import jikanjson
from cogs.MyAnimeList.getname import getname
from cogs.MyAnimeList.results import results
from cogs.MyAnimeList.selection import selection
#from cogs.MyAnimeList.user import userstatus, jikanjson, favorites
from cogs.MyAnimeList.search import Search
from cogs.MyAnimeList.malcmd import MALcmd
#from cogs.MyAnimeList.meta import Help
from cogs.Pexels.pexels import Pexels
from cogs.BeeBee.beebee import BB
from cogs.Leonardo.leonardo import Leonardo
from cogs.Anime.anime import Anime
from cogs.Emoji.emoji import EmojiCog
from cogs.Marblex.prices import MarblexCog
from cogs.User.echo import Echo
from cogs.User.snipe import Snipe
from cogs.NNK.redeem import CouponCog
from cogs.NNK.helpme import HelpMe
from cogs.Utility.roll import RollCog


# Set up logging.
logging.basicConfig(filename='bot.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Load the bot configuration
token = os.environ.get('TOKEN')
prefix = os.environ.get('PREFIX')

# Create an Intents object with default intents
intents = discord.Intents.all()

# Create an instance of Bot using intents
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None, case_insensitive=True)

@bot.event
async def on_ready():
    your_user_id = bot.user.id
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'Logged in as {Fore.YELLOW}{bot.user.name}{Fore.RESET}')
    logging.info(f'Bot ID {Fore.YELLOW}{bot.user.id}{Fore.RESET}')
    logging.info(f'Discord Version {Fore.YELLOW}{discord.__version__}{Fore.RESET}')
    logging.info(f'Python Version {Fore.YELLOW}{platform.python_version()}{Fore.RESET}')
    
    await setup_cogs()
    logging.info(f'Slash CMDs Synced {Fore.YELLOW}{len(bot.commands)} Commands{Fore.RESET}')
    
    # Set a custom status for the bot
    custom_status = discord.Activity(name="Asdoni's OnlyFans...", type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.online, activity=custom_status)


    # Sync the commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

async def setup_cogs():
    cogslist = [Dingo(bot),
                BB(bot),
                Pexels(bot),
                MALcmd(bot),
                Character_Info(bot),
                Search(bot),
                Welcome(bot),
                PP(bot),
                Love(bot),
                Throw(bot),
                Trivia(bot),
                InfoCog(bot),
                ChatGPT(bot),
                TranslatorCog(bot),
                AvatarCog(bot),
                HornyCog(bot),
                Leonardo(bot),
                Anime(bot),
                EmojiCog(bot),
                MarblexCog(bot),
                Echo(bot),
                Snipe(bot),
                CouponCog(bot),
                HelpMe(bot),
                RollCog(bot),
                ]
    for ext in cogslist:
        try:
            await bot.add_cog(ext)
            logging.info(f"Loaded extension {ext}")
        except Exception as e:
            logging.error(f"Failed to load extension {ext}: {e}")

@bot.event
async def on_message(message):
    # Check if the message author is a bot
    if message.author.bot:
        return  # Ignore messages from bots

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    author_display_name = message.author.display_name

    # Check if the message has attachments
    if message.attachments:
        attachment_info = "Attachment: " + ", ".join(attachment.filename for attachment in message.attachments)
        print(f"{timestamp} - {author_display_name}: - {attachment_info}")
    else:
        print(f"{timestamp} - {author_display_name}: - {message.content}")

    await bot.process_commands(message)

# Start the bot
bot.run(token)
