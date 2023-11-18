import os
import discord
from discord import app_commands
from discord.ext import commands
import json
import logging


def is_allowed_role(ctx):
    allowed_roles = ['Admin', 'Best Egirls']
    user_roles = [role.name for role in ctx.user.roles]
    for role in allowed_roles:
        if role in user_roles:
            return True
    return False

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_message = None

        current_directory = os.path.dirname(os.path.abspath(__file__))
        welcome_json_path = os.path.join(current_directory, 'welcome.json')

        with open(welcome_json_path, 'r') as welcome_file:
            welcome_data = json.load(welcome_file)
            self.welcome_message = welcome_data.get('welcome_message', '')

        
    @app_commands.command(
            name='welcome', 
            description="Welcome a user to the server"
        )
    async def welcome(self, ctx, user: discord.User = None):
        if not is_allowed_role(ctx):
            await ctx.response.send_message("You don't have the required role to use this command.")
            return

        if user is None:
            await ctx.response.send_message("Incorrect syntax. Correct syntax: /welcome @user")
            return

        if user == ctx.user:
            await ctx.response.send_message("You cannot welcome yourself.")
            return

        if self.welcome_message:
            customized_welcome_message = self.welcome_message.replace("{user_mention}", user.mention)
            await ctx.response.send_message(customized_welcome_message)
        else:
            await ctx.response.send_message("Welcome to the server!")

"""     @app_commands.command(
            name='edit', 
            description="Edit the welcome message"
        )
    async def edit(self, ctx):
        if not is_allowed_role(ctx):
            await ctx.response.send_message("You don't have the required role to use this command.")
            return

        current_directory = os.path.dirname(os.path.abspath(__file__))
        welcome_json_path = os.path.join(current_directory, 'welcome.json')

        with open(welcome_json_path, 'r') as welcome_file:
            welcome_data = json.load(welcome_file)
            current_welcome_message = welcome_data.get('welcome_message', '')
            formatted_welcome_message = f"```\n{current_welcome_message}\n```"
            await ctx.response.send_message(f"Current welcome message:\n{formatted_welcome_message}\n\nPlease enter the new welcome message:")

            response = await self.bot.wait_for('message', check=lambda m: m.user == ctx.user)

            welcome_data['welcome_message'] = response.content
            with open(welcome_json_path, 'w') as welcome_file:
                json.dump(welcome_data, welcome_file, indent=4)
                await ctx.response.send_message("Welcome message updated successfully!")
 """
def setup(bot):
    bot.add_cog(Welcome(bot))