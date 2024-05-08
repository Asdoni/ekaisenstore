import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time, timezone
from discord.ui import TextInput, Modal

from .birthday_utilities import BirthdayUtilities
from bot import EGirlzStoreBot

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_utilities = BirthdayUtilities(bot.db, bot)
        self.daily_tasks.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.daily_tasks.is_running():
            self.daily_tasks.start()

    async def on_member_remove(self, member):
        response = await self.birthday_utilities.delete_birthday(member.guild.id, member.id)
        print(f"Birthday data deletion response for {member}: {response}")

    def cog_unload(self):
        self.daily_tasks.cancel()

    @tasks.loop(time=time(0, 0))
    async def daily_tasks(self):
        now = datetime.now(timezone.utc)
        print(f"Task running at: {now}")
        for guild in self.bot.guilds:
            role = await self.birthday_utilities.ensure_birthday_role(guild)
            if not role:
                continue

            channel_id = await self.birthday_utilities.get_birthday_channel(guild.id)
            if not channel_id:
                print(f"No birthday channel set for {guild.name}.")
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                print(f"Channel ID {channel_id} not found in {guild.name}.")
                continue

            todays_birthdays = await self.birthday_utilities.get_birthdays_on_date(guild.id, now.month, now.day)
            yesterdays_birthdays = await self.birthday_utilities.get_birthdays_on_date(guild.id, now.month, now.day - 1)
            print(f"Today's Birthdays in {guild.name}: {todays_birthdays}")
            print(f"Yesterday's Birthdays in {guild.name}: {yesterdays_birthdays}")

            for user_info in yesterdays_birthdays:
                user = guild.get_member(int(user_info['user_id']))
                if user and role in user.roles:
                    await user.remove_roles(role)
                    print(f"Removed birthday role from {user.display_name}.")

            for user_info in todays_birthdays:
                user = guild.get_member(int(user_info['user_id']))
                if user:
                    await user.add_roles(role)
                    print(f"Assigned birthday role to {user.display_name}.")
                    await self.announce_birthday(user, role, guild.id, now, channel)

            if now.month == 2 and now.day == 28 and not BirthdayUtilities.is_leap_year(now.year):
                feb_29_birthdays = await self.birthday_utilities.get_birthdays_on_date(guild.id, 2, 29)
                for user_info in feb_29_birthdays:
                    user = guild.get_member(int(user_info['user_id']))
                    if user:
                        await user.add_roles(role)
                        print(f"Assigned birthday role to {user.display_name} for Feb 29 on non-leap year.")
                        await self.announce_birthday(user, role, guild.id, now, channel)

            for user_info in yesterdays_birthdays:
                user = guild.get_member(int(user_info['user_id']))
                if user and role in user.roles:
                    await user.remove_roles(role)
                    print(f"Removed birthday role from {user.display_name}.")

            for user_info in todays_birthdays:
                user = guild.get_member(int(user_info['user_id']))
                if user and role not in user.roles:
                    await user.add_roles(role)
                    print(f"Assigned birthday role to {user.display_name}.")
                    await self.announce_birthday(user, role, guild.id, now, channel)

    async def announce_birthday(self, user, role, guild_id, now, channel):
        try:
            print(f"Preparing to announce for {user.display_name} in {channel.guild.name}.")
            await user.add_roles(role)
            print(f"Role {role.name} added to {user.display_name}.")

            custom_message = await self.birthday_utilities.get_birthday_message(guild_id) or "Happy Birthday!"
            birthday_data = await self.birthday_utilities.get_birthday(guild_id, user.id)

            if birthday_data and isinstance(birthday_data, dict):
                birthday_str = f"{birthday_data['day']:02d}/{birthday_data['month']:02d}"
                if birthday_data['year'] > 1:
                    birthday_str += f"/{birthday_data['year']}"
                message = f"{custom_message} {birthday_data['mention']} - {birthday_str} 🎉"

                embed = discord.Embed(title="Birthday Announcement!", description=message, color=discord.Color.blue())
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text="Birthday Announcement by EGirlzStore Bot ©")

                print(f"Sending birthday announcement for {user.display_name} to {channel.name}.")
                await channel.send(embed=embed)
                print(f"Birthday announcement posted for {user.display_name}.")
            else:
                print("Invalid or incomplete birthday data:", birthday_data)

        except Exception as e:
            print(f"Failed to announce birthday for {user.display_name}: {e}")

    @daily_tasks.before_loop
    async def before_birthday_announcer(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="birthday", description="Manage your birthday settings")
    async def birthday_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Birthday Management", description="Choose an option below to manage your birthday settings.", color=discord.Color.blue())
        embed.add_field(name="Set Birthday", value="Enter your birthday using the DD/MM/YYYY format.\nYear is optional.", inline=False)
        embed.add_field(name="Delete Birthday", value="Deletes your birthday.", inline=False)
        embed.add_field(name="Show Birthday", value="View a user's birthday.", inline=False)
        embed.add_field(name="List Birthdays", value="View all birthdays.", inline=False)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="Birthday Management by EGirlzStore Bot ©")

        view = BirthdayView(self.bot, interaction.user, self.birthday_utilities)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @app_commands.command(name="adminbday", description="Admin settings for birthday management")
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def admin_birthday_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Admin Birthday Management", description="Select an admin option below for birthday settings.", color=discord.Color.gold())
        embed.add_field(name="Set Channel", value="Set the channel for birthday announcements.", inline=False)
        embed.add_field(name="Unset Channel", value="Remove the birthday announcement channel.", inline=False)
        embed.add_field(name="Set Message", value="Set a custom birthday message.", inline=False)
        embed.add_field(name="Delete Message", value="Remove the custom birthday message.", inline=False)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="Admin Birthday Management by EGirlzStore Bot ©")

        view = AdminBirthdayView(self.bot, self.birthday_utilities, interaction.guild, interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MemberSearchModal(discord.ui.Modal):
    def __init__(self, bot, birthday_utilities, guild, manage=False):
        super().__init__(title="Search User")
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.guild = guild
        self.manage = manage

        self.add_item(TextInput(label="Enter user name", placeholder="Type a part of the user's name"))

    async def on_submit(self, interaction: discord.Interaction):
        search_input = self.children[0].value.lower()
        members = [member for member in self.guild.members if search_input in member.display_name.lower() and not member.bot]

        if members:
            options = [discord.SelectOption(label=member.display_name, value=str(member.id), description=f"ID: {member.id}") for member in members[:25]]
            select = discord.ui.Select(options=options, placeholder="Select a member")

            async def select_callback(interaction: discord.Interaction):
                member_id = select.values[0]
                member = self.guild.get_member(int(member_id))
                if member:
                    if self.manage:
                        view = ManageBirthdayOptions(self.bot, self.birthday_utilities, self.guild, member)
                        await interaction.response.edit_message(content=f"Manage birthday for {member.display_name}:", view=view)
                    else:
                        birthday_info = await self.birthday_utilities.get_birthday(interaction.guild.id, member.id)
                        if birthday_info:
                            await interaction.response.edit_message(content=birthday_info, view=None)
                        else:
                            await interaction.response.send_message("Birthday information not found.", ephemeral=True)
                else:
                    await interaction.response.send_message("Member not found.", ephemeral=True)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.edit_message(content="Select the member:", embed=None, view=view)
        else:
            await interaction.response.send_message("No members found.", ephemeral=True)

class ChannelSearchModal(discord.ui.Modal):
    def __init__(self, bot, birthday_utilities, admin_view):
        super().__init__(title="Search Channel")
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.admin_view = admin_view
        self.selected_channel_id = None

        self.add_item(TextInput(label="Enter channel name", placeholder="Type a part of the channel's name"))

    async def on_submit(self, interaction: discord.Interaction):
        search_input = self.children[0].value.lower()
        channels = [channel for channel in interaction.guild.channels if search_input in channel.name.lower() and isinstance(channel, discord.TextChannel)]
        
        if channels:
            options = [discord.SelectOption(label=channel.name, value=str(channel.id), description=f"ID: {channel.id}") for channel in channels[:25]]
            select = discord.ui.Select(options=options, placeholder="Select a channel")

            async def select_callback(inner_interaction: discord.Interaction):
                selected_channel_id = select.values[0]
                await self.handle_channel_selection(inner_interaction, selected_channel_id)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.edit_message(content="Select the channel:", embed=None, view=view)
        else:
            await interaction.response.send_message("No channels found with that name.", ephemeral=True)

    async def handle_channel_selection(self, interaction, channel_id):
        channel_id = int(channel_id)
        response = await self.birthday_utilities.set_birthday_channel(interaction.guild.id, channel_id)
        await interaction.response.edit_message(content=response, view=None)
        
        await self.admin_view.post_birthday_list(interaction)


class BirthdayModal(Modal):
    def __init__(self, bot, birthday_utilities, title='Enter Birthday Details'):
        super().__init__(title=title)
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.add_item(TextInput(
            label="Enter your Birthday",
            placeholder="DD/MM, DD/MM/YY, or DD/MM/YYYY",
            style=discord.TextStyle.short
            
        ))
        self.message = None

    async def send_initial_message(self, channel, content):
        self.message = await channel.send(content, view=self)
        print(f"Message sent and stored: {self.message.id}")

    async def on_timeout(self):
        print("Timeout occurred")
        await BirthdayUtilities.delete_message_on_timeout(self.bot, self.message)

    async def on_submit(self, interaction: discord.Interaction):
        birthday_input = self.children[0].value
        print(f"Modal submitted with input: {birthday_input}")
        
        birthday_date, error_msg = BirthdayUtilities.parse_birthday(birthday_input)
        if error_msg:
            print(f"Error returned from parse_birthday: {error_msg}")
            await interaction.response.send_message(content=error_msg, ephemeral=True)
            await asyncio.sleep(15)
            await interaction.delete_original_response()
            return

        response = await self.birthday_utilities.register_birthday(interaction.guild.id, interaction.user.id, birthday_date)
        await interaction.response.edit_message(content=response, view=None, embed=None)
        try:
            await asyncio.sleep(15)
            await interaction.delete_original_response()        
        except Exception as e:
            print(f"Failed to delete original response: {str(e)}")

class MessageModal(discord.ui.Modal, title="Set Message"):
    def __init__(self, bot, birthday_utilities, delete=False):
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.delete = delete
        super().__init__()

    message = discord.ui.TextInput(label="Enter Message", style=discord.TextStyle.long, placeholder="Happy birthday!")

    async def on_submit(self, interaction: discord.Interaction):
        message = self.message.value
        if self.delete:
            response = await self.birthday_utilities.delete_birthday_message(interaction.guild_id, message)
        else:
            response = await self.birthday_utilities.set_birthday_message(interaction.guild_id, message)

        await interaction.response.edit_message(content=response, embed=None, view=None)
        await asyncio.sleep(15)
        await interaction.delete_original_response()

class UserModal(discord.ui.Modal):
    def __init__(self, bot, guild, birthday_utilities, title, user_id, initial_date=None):
        super().__init__(title=title)
        self.bot = bot
        self.guild = guild
        self.birthday_utilities = birthday_utilities
        self.user_id = user_id
        self.add_item(TextInput(
            label="Enter Birthday", 
            placeholder="DD/MM, DD/MM/YY, or DD/MM/YYYY",
            default=initial_date,
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        birthday_input = self.children[0].value
        birthday_date, error_msg = BirthdayUtilities.parse_birthday(birthday_input)
        if error_msg:
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        response = await self.birthday_utilities.register_birthday(self.guild.id, self.user_id, birthday_date)
        await interaction.response.edit_message(content=f"Birthday set successfully for {interaction.guild.get_member(self.user_id).display_name}.", view=None)
        await asyncio.sleep(15)
        await interaction.delete_original_response()

class UserSelectMenu(discord.ui.Select):
    def __init__(self, bot, birthday_utilities, guild, action):
        super().__init__(placeholder="Choose a member...", min_values=1, max_values=1)
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.action = action
        self.guild = guild

        members = [member for member in guild.members if not member.bot]
        self.options = [discord.SelectOption(label=member.display_name, description=f"ID: {member.id}", value=str(member.id)) for member in members]

    async def callback(self, interaction: discord.Interaction):
        member_id = int(self.values[0])
        member = self.guild.get_member(member_id)
        if member:
            if self.action == 'show':
                birthday_data = await self.birthday_utilities.get_birthday(interaction.guild.id, member_id)

                if birthday_data:
                    try:
                        birthday = datetime(year=birthday_data['birth_year'], month=birthday_data['birth_month'], day=birthday_data['birth_day'])
                        birthday_formatted = BirthdayUtilities.format_birthday(birthday, birthday_data['birth_year'])
                        description = f"{member.mention}'s Birthday: {birthday_formatted}"
                    except Exception as e:
                        description = f"Error creating birthday datetime: {str(e)}"
                else:
                    description = f"No birthday information found for {member.mention}."

                await interaction.response.edit_message(content=description, embed=None, view=None)
            elif self.action == 'manage':
                view = ManageBirthdayOptions(self.bot, self.birthday_utilities, self.guild, member)
                await interaction.response.edit_message(content=f"Manage birthday for {member.mention}:", view=view)
            else:
                description = f"No birthday information found for {member.mention}."
        else:
            await interaction.response.edit_message(content="Member not found.", view=None)

class ManageBirthdayOptions(discord.ui.View):
    def __init__(self, bot, birthday_utilities, guild, member):
        super().__init__()
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.guild = guild
        self.member = member

        set_birthday_button = discord.ui.Button(label="Set Birthday", style=discord.ButtonStyle.green, custom_id="set_birthday")
        delete_birthday_button = discord.ui.Button(label="Delete Birthday", style=discord.ButtonStyle.red, custom_id="delete_birthday")
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.grey, custom_id="cancel_birthday")

        set_birthday_button.callback = self.set_birthday
        delete_birthday_button.callback = self.delete_birthday
        cancel_button.callback = self.cancel

        self.add_item(set_birthday_button)
        self.add_item(delete_birthday_button)
        self.add_item(cancel_button)

    async def set_birthday(self, interaction: discord.Interaction):
        current_birthday = await self.birthday_utilities.get_birthday(self.guild.id, self.member.id)
        if current_birthday and isinstance(current_birthday, dict):
            if all (key in current_birthday for key in ('birth_day', 'birth_month', 'birth_year')):
                initial_date = f"{current_birthday['birth_day']:02d}/{current_birthday['birth_month']:02d}/{current_birthday['birth_year']}"
            else:
                initial_date = ""
        else:
            initial_date = "" 

        modal = UserModal(self.bot, self.guild, self.birthday_utilities, "Set Birthday for " + self.member.mention, self.member.id, initial_date=initial_date)
        await interaction.response.send_modal(modal)

    async def delete_birthday(self, interaction: discord.Interaction):
        response = await self.birthday_utilities.delete_birthday(interaction.guild_id, interaction.user.id)
        if response.startswith("Birthday deleted for"):
            await interaction.response.send_message(response, ephemeral=True)
        else:
            await interaction.response.send_message(response, ephemeral=True)
        await self.birthday_utilities.update_birthday_list_message_id(interaction.guild_id)
        await asyncio.sleep(15)
        await interaction.delete_original_response()

    async def cancel(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Birthday management canceled.", view=None)
        await asyncio.sleep(15)
        await interaction.delete_original_response()


class UserSelectView(discord.ui.View):
    def __init__(self, bot, birthday_utilities, guild, options):
        super().__init__()
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.guild = guild
        select = discord.ui.Select(options=options, placeholder="Select a user to manage...")
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        user_id = interaction.data['values'][0]
        user = self.guild.get_member(int(user_id))
        if user:
            manage_options_view = ManageBirthdayOptions(self.bot, self.birthday_utilities, self.guild, user)
            await interaction.response.edit_message(content=f"Manage birthday for {user.display_name}:", view=manage_options_view)
        else:
            await interaction.followup.send("User not found.", ephemeral=True)

class BirthdayView(discord.ui.View):
    def __init__(self, bot, user, birthday_utilities):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.birthday_utilities = birthday_utilities
        self.message = None

    async def send_initial_message(self, channel, content):
        self.message = await channel.send(content, view=self)
        print(f"Message sent and stored: {self.message.id}")

    async def on_timeout(self):
        print("Timeout occurred")
        await BirthdayUtilities.delete_message_on_timeout(self.bot, self.message)

    @discord.ui.button(label="Set Birthday", style=discord.ButtonStyle.green)
    async def set_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BirthdayModal(self.bot, self.birthday_utilities)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete Birthday", style=discord.ButtonStyle.red)
    async def delete_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = await self.birthday_utilities.delete_birthday(interaction.guild_id, interaction.user.id)
        await interaction.response.edit_message(content=response, embed=None, view=None)
        await asyncio.sleep(15)
        await interaction.delete_original_response()

    @discord.ui.button(label="Show Birthday", style=discord.ButtonStyle.blurple)
    async def show_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MemberSearchModal(self.bot, self.birthday_utilities, interaction.guild, manage=False)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="List Birthdays", style=discord.ButtonStyle.grey)
    async def list_birthdays(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        birthdays = await self.birthday_utilities.get_birthdays(guild_id)
        birthday_dict = {}
        current_year = datetime.now().year

        for data in birthdays:
            print(f"Processing data: {data}")
            if 'birth_year' in data and 'birth_month' in data and 'birth_day' in data:
                year, month, day = data['birth_year'], data['birth_month'], data['birth_day']
                birthday = datetime(year if year > 1 else current_year, month, day)
                birthday_str = birthday.strftime("%d/%m" if year == 1 else "%d/%m/%Y")
                month_name = birthday.strftime("%B")
                if month_name not in birthday_dict:
                    birthday_dict[month_name] = []
                user = interaction.guild.get_member(int(data["user_id"]))
                if user:
                    birthday_display = f"{user.mention} {birthday_str}"
                    birthday_dict[month_name].append(birthday_display)
            else:
                print(f"Missing key data in: {data}")

        embed = discord.Embed(title=f"🎂 Birthday List - {interaction.guild.name}", description="Here are the registered birthdays:", color=discord.Color.gold())
        if interaction.guild.icon:
            embed.set_footer(text="List of birthdays 📅")
            embed.set_thumbnail(url=interaction.guild.icon.url)

        for month in sorted(birthday_dict.keys(), key=lambda x: datetime.strptime(x, "%B")):
            if birthday_dict[month]:
                month_birthdays = "\n".join(birthday_dict[month])
                embed.add_field(name=month, value=month_birthdays, inline=False)

        if not birthday_dict:
            embed.description += "\n\nNo birthdays registered yet!"

        await interaction.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(180)
        try:
            await interaction.delete_original_response()
        except discord.NotFound:
            pass

class ConfirmView(discord.ui.View):
    def __init__(self, confirm_callback, cancel_callback):
        super().__init__()
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirm_callback(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cancel_callback(interaction)

class AdminBirthdayView(discord.ui.View):
    def __init__(self, bot, birthday_utilities, guild, interaction):
        super().__init__(timeout=180)
        self.bot = bot
        self.birthday_utilities = birthday_utilities
        self.guild = guild
        self.interaction = interaction
        self.message = None

        members = [member for member in guild.members if not member.bot]

        self.set_user_birthday_view = UserSelectMenu(self.bot, self.birthday_utilities, self.guild, 'set')
        self.delete_user_birthday_view = UserSelectMenu(self.bot, self.birthday_utilities, self.guild, 'delete')

    async def replace_birthday_list(self, message_id, channel, embed, interaction):
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            await interaction.response.edit_message(content="Birthday list updated successfully!", embed=None, view=None)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            await self.birthday_utilities.update_birthday_list_message_id(interaction.guild.id, message.id)
            await interaction.response.edit_message(content="Original message not found, posted as a new message and updated message ID.", embed=None, view=None)
        except Exception as e:
            await interaction.response.send_message(content=f"Failed to update birthday list: {str(e)}", ephemeral=True)

    async def post_birthday_list(self, interaction):
        guild_id = interaction.guild.id
        channel_id = await self.birthday_utilities.get_birthday_channel(guild_id)
        if not channel_id:
            await interaction.response.send_message(content="No channel set for birthday announcements.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(content="The set channel was not found or the bot lacks access.", ephemeral=True)
            return

        birthday_dict = await self.birthday_utilities.prepare_birthday_data(guild_id)
        embed = self.birthday_utilities.prepare_birthday_list_embed(interaction, birthday_dict)
        settings = await self.birthday_utilities.get_guild_settings(guild_id)
        message_id = settings.get('birthday_list_message_id')

        if message_id:
            message = None
            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                pass 

            if message:
                confirm_view = ConfirmView(
                    confirm_callback=lambda i: self.replace_birthday_list(message_id, channel, embed, i),
                    cancel_callback=lambda i: self.cancel_operation(i)
                )
                await interaction.followup.send(content=f"A birthday list message already exists in {channel.mention}. Would you like to update it?\nMessage: {message.jump_url}", view=confirm_view, ephemeral=True)
            else:
                new_message = await channel.send(embed=embed)
                await self.birthday_utilities.update_birthday_list_message_id(guild_id, new_message.id)
                await interaction.followup.send(content=f"Posted new birthday list and updated message ID in {channel.mention}\nMessage: {new_message.jump_url}", ephemeral=True)
        else:
            new_message = await channel.send(embed=embed)
            await self.birthday_utilities.update_birthday_list_message_id(guild_id, new_message.id)
            await interaction.followup.send(content=f"Birthday list posted successfully in {channel.mention}\nMessage: {new_message.jump_url}", ephemeral=True)

    async def replace_birthday_list(self, message_id, channel, embed, interaction):
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            await interaction.response.edit_message(content=f"Birthday list updated successfully in {channel.mention}\nMessage: {message.jump_url}", embed=None, view=None, ephemeral=True)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            await interaction.response.edit_message(content=f"Original message not found, posted as a new message in {channel.mention}\nMessage: {message.jump_url}", embed=None, view=None, ephemeral=True)


    async def cancel_operation(self, interaction: discord.Interaction):
        try:
            await interaction.response.edit_message(content="Post List operation canceled.", view=None)
        except Exception as e:
            print(f"Failed to edit the original response: {e}")


    async def send_initial_message(self, channel, content):
        self.message = await channel.send(content, view=self)
        print(f"Message sent and stored: {self.message.id}")

    async def on_timeout(self):
        print("Timeout occurred")
        await BirthdayUtilities.delete_message_on_timeout(self.bot, self.message)

    @discord.ui.button(label="Set Channel", style=discord.ButtonStyle.green)
    async def set_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChannelSearchModal(self.bot, self.birthday_utilities, self)
        await interaction.response.send_modal(modal)

        await modal.wait() 

        if modal.selected_channel_id:
            new_channel_id = modal.selected_channel_id
            response = await self.set_birthday_channel(interaction.guild.id, new_channel_id)
            await interaction.followup.send(response)

            await self.post_birthday_list(interaction)

    async def channel_select_callback(self, interaction: discord.Interaction):
        new_channel_id = int(interaction.data['values'][0])
        new_channel = interaction.guild.get_channel(new_channel_id)
        if not new_channel:
            await interaction.response.send_message("Selected channel is invalid.", ephemeral=True)
            return

        settings = await self.birthday_utilities.get_guild_settings(interaction.guild.id)
        old_channel_id = settings.get('birthday_channel')
        old_message_id = settings.get('birthday_list_message_id')

        try:
            response = await self.birthday_utilities.set_birthday_channel(interaction.guild.id, new_channel_id)
            await interaction.response.send_message(f"Channel set successfully: {response}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error setting channel: {e}", ephemeral=True)
            await interaction.response.send_message("Failed to set the channel.", ephemeral=True)
            return
        
        if old_channel_id and old_message_id:
            old_channel = interaction.guild.get_channel(old_channel_id)
            if old_channel:
                try:
                    old_message = await old_channel.fetch_message(old_message_id)
                    await old_message.delete()
                except discord.NotFound:
                    print("Old message not found, nothing to delete.")
        
        birthday_dict = await self.birthday_utilities.prepare_birthday_data(interaction.guild.id)
        embed = self.birthday_utilities.prepare_birthday_list_embed(interaction, birthday_dict)
        new_message = await new_channel.send(embed=embed)
        
        await self.birthday_utilities.update_birthday_list_message_id(interaction.guild.id, new_message.id)

        await interaction.response.edit_message(content=f"Birthday channel set to {new_channel.mention} and message updated.", view=None)
        await asyncio.sleep(15)
        try:
            await interaction.delete_original_response()
        except discord.NotFound:
            pass

    @discord.ui.button(label="Unset Channel", style=discord.ButtonStyle.red)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        confirm_button = discord.ui.Button(label="Confirm Delete", style=discord.ButtonStyle.red, custom_id="confirm_delete_channel")
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_delete_channel")

        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.edit_message(content="Are you sure you want to delete the birthday announcement channel?", embed=None, view=view)

        confirm_button.callback = self.confirm_delete_channel
        cancel_button.callback = self.cancel_delete_channel

    async def confirm_delete_channel(self, interaction: discord.Interaction):
        try:
            response = await self.birthday_utilities.delete_birthday_channel(interaction.guild.id)
            await interaction.response.edit_message(content=f"Channel deleted successfully: {response}", view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()
        except Exception as e:
            print(f"Failed to Unset channel: {e}")
            await interaction.response.edit_message(content="Failed to delete the channel.", view=None)

    async def cancel_delete_channel(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Channel deletion canceled.", view=None)

    @discord.ui.button(label="Set Message", style=discord.ButtonStyle.blurple)
    async def set_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MessageModal(self.bot, self.birthday_utilities)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete Message", style=discord.ButtonStyle.red)
    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        confirm_button = discord.ui.Button(label="Confirm Delete", style=discord.ButtonStyle.red, custom_id="confirm_delete_message")
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_delete_message")

        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.edit_message(content="Are you sure you want to delete the birthday message?", embed=None, view=view)
        
        confirm_button.callback = self.confirm_delete_message
        cancel_button.callback = self.cancel_delete_message

    async def confirm_delete_message(self, interaction: discord.Interaction):
        try:
            response = await self.birthday_utilities.delete_birthday_message(interaction.guild.id)
            await interaction.response.edit_message(content=f"{response}", view=None)
            await asyncio.sleep(15)
            await interaction.delete_original_response()
        except Exception as e:
            print(f"Failed to delete message: {e}")
            await interaction.response.edit_message(content="Failed to delete the Message.", view=None)

    async def cancel_delete_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Message deletion canceled.", view=None)

    @discord.ui.button(label="Manage User Birthday", style=discord.ButtonStyle.blurple)
    async def manage_user_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MemberSearchModal(self.bot, self.birthday_utilities, interaction.guild, manage=True)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Post List", style=discord.ButtonStyle.blurple)
    async def post_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.post_birthday_list(interaction)

    async def confirm_post_list(self, interaction: discord.Interaction):
        await self.post_birthday_list(interaction)

    async def cancel_post_list(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="List posting canceled.", view=None)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Birthday(bot))