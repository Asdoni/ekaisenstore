import os
import discord
from discord.ext import commands

# Load the bot configuration
token = os.environ.get('TOKEN')
prefix = os.environ.get('PREFIX')

# Create an Intents object with default intents
intents = discord.Intents.all()

# Create an instance of Bot using intents
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None, case_insensitive=True)
