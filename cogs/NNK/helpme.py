import os
import re
import discord
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from datetime import datetime, timedelta, timezone
import aiomysql
import logging

# Define the channel ID for reminders
REMINDER_CHANNEL_ID = 1173024685882081280

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
}

class HelpMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_sessions = {}

    async def db_execute(self, query, params=None):
        async with aiomysql.create_pool(**DB_CONFIG) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
                    return await cursor.fetchall()
    
    async def get_user_preference(self, user_id):
        query = "SELECT pm FROM user_pm_preferences WHERE user_id = %s"
        result = await self.db_execute(query, (user_id,))
        return result[0]['pm'] if result else 0


    async def set_user_preference(self, user_id, preference):
        query = "INSERT INTO user_pm_preferences (user_id, pm) VALUES (%s, %s) ON DUPLICATE KEY UPDATE pm = %s"
        await self.db_execute(query, (user_id, preference, preference))

    # The helpme command is a method inside the HelpMe class
    @app_commands.command(name="helpme", description="Ask members to help you")
    @app_commands.describe(
        event_type="The type of event",
        event_date="The date of the event (YYYY-MM-DD)",
        event_time="The time of the event (UTC, format: HH:MM)",
        description="Additional details about the event (optional)"
    )
    @app_commands.choices(
        event_type=[
            app_commands.Choice(name="WorldBoss: Ardor", value="Ardor"),
            app_commands.Choice(name="WorldBoss: Acteon", value="Acteon"),
            app_commands.Choice(name="Dimensional Border: Volcanord", value="Volcanord"),
            app_commands.Choice(name="Dimensional Border: Natrum", value="Natrum"),
            app_commands.Choice(name="Dimensional Border: Proto Mark 13", value="Proto Mark 13"),
            app_commands.Choice(name="Interstellar: Pisces", value="Pisces"),
            app_commands.Choice(name="Interstellar: Aires", value="Aires"),
            app_commands.Choice(name="Interstellar: Scorpio", value="Scorpio")
        ],
        event_date=[app_commands.Choice(name=(datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d"), value=(datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(0, 8)],
    )
    async def helpme(self, interaction: Interaction, event_type: str, event_date: str, event_time: str, description: str = "", ranked: bool = False):
        if ranked and event_type not in ["Pisces", "Aires", "Scorpio"]:
            await interaction.response.send_message("Ranked option is only available for Interstellar events.", ephemeral=True)
            return
        
        # Validate the event_time format (HH:MM)
        if not re.match(r"^\d{2}:\d{2}$", event_time):
            await interaction.response.send_message("Please enter the time in HH:MM format.", ephemeral=True)
            return

        # Parse the event date and time in UTC
        event_datetime_str = f"{event_date} {event_time}"
        event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

        # Check if the event is ranked and append to the title
        title_suffix = " Ranked" if ranked else ""
        embed_title = f"Help Me: {event_type}{title_suffix}"

        # Get the current time in UTC
        now_utc = datetime.now(timezone.utc)

        if event_datetime <= now_utc:
            await interaction.response.send_message("The event time must be in the future.", ephemeral=True)
            return

        # Convert event_datetime to Unix timestamp and then to Discord timestamp format
        event_timestamp = int(event_datetime.timestamp())

        # Inside helpme, when initializing the embed description
        embed_description = f"Event Date: <t:{event_timestamp}:d>\nEvent Time: <t:{event_timestamp}:t>\n\n**Participants (Max 5):**\n• {interaction.user.mention}\n"
        if description:
            embed_description = f"{description}\n\n" + embed_description

        embed = Embed(title=embed_title, description=embed_description, color=discord.Color.blue())

        # Button for joining
        join_button = Button(label="Join", style=ButtonStyle.green)
        join_button.callback = self.join_callback

        # Button for leaving
        leave_button = Button(label="Leave", style=ButtonStyle.red)
        leave_button.callback = self.leave_callback

        # Button for deleting the event (visible only to the creator)
        delete_button = Button(label="Delete Event", style=ButtonStyle.danger)
        delete_button.callback = self.delete_event

        # Create buttons for the embed
        join_button = Button(label="Join", style=ButtonStyle.green)
        join_button.callback = self.join_callback
        leave_button = Button(label="Leave", style=ButtonStyle.red)
        leave_button.callback = self.leave_callback
        delete_button = Button(label="Delete Event", style=ButtonStyle.danger)
        delete_button.callback = self.delete_event

        # Create a view and add the buttons to it
        view = View(timeout=None)
        view.add_item(join_button)
        view.add_item(leave_button)
        view.add_item(delete_button)

        # Fetch the specific channel using REMINDER_CHANNEL_ID
        reminder_channel = self.bot.get_channel(REMINDER_CHANNEL_ID)

        if reminder_channel:
            # Send the embed message with buttons to the reminder channel
            message = await reminder_channel.send(embed=embed, view=view)
            message_id = message.id
            
            # Save the session with additional context using the message ID
            self.help_sessions[message_id] = {
                "embed": embed,
                "members": [interaction.user],
                "join_button": join_button,
                "leave_button": leave_button,
                "delete_button": delete_button,
                "initiator_id": interaction.user.id,
                "channel_id": REMINDER_CHANNEL_ID
            }

            # Schedule the reminder as a background task using the message ID
            self.bot.loop.create_task(self.send_reminder(message_id, event_datetime))

    async def join_callback(self, button_interaction: Interaction):
        message_id = button_interaction.message.id
        user_id = button_interaction.user.id
        session = self.help_sessions.get(message_id)
        if session:
            if user_id in [member.id for member in session['members']]:
                await button_interaction.response.send_message("You are already in the event.", ephemeral=True)
            elif len(session['members']) >= 5:
                await button_interaction.response.send_message("The event is full.", ephemeral=True)
            else:
                session['members'].append(button_interaction.user)
                session['embed'].description += f"• {button_interaction.user.mention}\n"
                await button_interaction.message.edit(embed=session['embed'])
                await button_interaction.response.defer()

    async def leave_callback(self, button_interaction: Interaction):
        message_id = button_interaction.message.id
        user_id = button_interaction.user.id
        session = self.help_sessions.get(message_id)
        if session:
            if user_id == session["initiator_id"]:
                await button_interaction.response.send_message("You cannot leave the event as you are the initiator.", ephemeral=True)
            elif button_interaction.user not in session['members']:
                await button_interaction.response.send_message("You are not part of this event.", ephemeral=True)
            else:
                session['members'].remove(button_interaction.user)
                session['embed'].description = session['embed'].description.replace(f"• {button_interaction.user.mention}\n", "")
                await button_interaction.message.edit(embed=session['embed'])
                await button_interaction.response.defer()

    async def delete_event(self, button_interaction: Interaction):
        session_id = button_interaction.message.id
        if session_id in self.help_sessions:
            if button_interaction.user.id == self.help_sessions[session_id]["initiator_id"]:
                del self.help_sessions[session_id]
                await button_interaction.message.delete()
            else:
                await button_interaction.response.send_message("You cannot delete this event as you are not the initiator.", ephemeral=True)

    def create_view(self, message_id, user_id):
        view = View(timeout=None)
        session = self.help_sessions.get(message_id)
        if session:
            # Add the "Join" button
            view.add_item(session["join_button"])

            # Add the "Leave" button
            view.add_item(session["leave_button"])

            # Add the "Delete Event" button
            view.add_item(session["delete_button"])

        return view

    async def send_reminder(self, message_id, event_datetime):
        now_utc = datetime.now(timezone.utc)
        wait_time = (event_datetime - now_utc).total_seconds()
        await asyncio.sleep(wait_time)

        session = self.help_sessions.get(message_id)
        if session:
            channel = self.bot.get_channel(session['channel_id'])
            if channel:
                member_mentions = ' '.join(member.mention for member in session['members'])
                if member_mentions:
                    await channel.send(f"Event starting! {member_mentions}")
                for member in session['members']:
                    if await self.get_user_preference(member.id):
                        try:
                            await member.send(f"Reminder: Your event '{session['embed'].title}' is starting!")
                        except discord.Forbidden:
                            logging.warning(f"Failed to send DM to {member.name}")
                        except Exception as e:
                            logging.error(f"Error sending DM to {member.name}: {e}")

        # Delete the event and reminder after one hour
        await asyncio.sleep(10)  # Wait for 1 hour after the event - 3600 seconds
        session = self.help_sessions.pop(message_id, None)
        if session:
            channel = self.bot.get_channel(session[REMINDER_CHANNEL_ID])
            if channel:
                message = await channel.fetch_message(message_id)
                await message.delete()

    # New command for toggling direct message preferences
    @app_commands.command(name="pm", description="Toggle direct message notifications for events")
    async def toggle_pm(self, interaction: Interaction, set: bool):
        await self.set_user_preference(interaction.user.id, 1 if set else 0)
        await interaction.response.send_message(f"Direct message notifications have been {'enabled' if set else 'disabled'}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpMe(bot))