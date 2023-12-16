import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone

from discord import app_commands, Interaction, Embed, ButtonStyle, Color, Forbidden
from discord.ext import commands
from discord.ui import Button, View
from bot import EGirlzStoreBot

# Global constant for the channel ID where reminders will be sent
REMINDER_CHANNEL_ID = 1178681796775387197


class HelpMe(commands.Cog):
    """ A cog to manage event help requests in a Discord server. """

    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.help_sessions = {}

    async def get_user_preference(self, user_id: int) -> bool:
        """ Retrieve user's preference for receiving private messages. """
        result = await self.bot.db.fetchone(f"SELECT pm FROM user_pm_preferences WHERE user_id = {user_id}")
        return bool(result[0]) if result else False

    async def set_user_preference(self, user_id: int, preference: bool):
        """ Update user's preference for receiving private messages. """
        await self.bot.db.commit(
            f"REPLACE INTO user_pm_preferences (user_id, pm) VALUES ({user_id}, {int(preference)})"
        )

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
            app_commands.Choice(name="Dimensional Hero", value="Dimensional Hero"),
            app_commands.Choice(name="Interstellar: Pisces", value="Pisces"),
            app_commands.Choice(name="Interstellar: Aries", value="Aries"),
            app_commands.Choice(name="Interstellar: Scorpio", value="Scorpio")
        ],
        event_date=[app_commands.Choice(
            name=(datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d"),
            value=(datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d")
        ) for i in range(0, 8)],
    )
    async def helpme(
            self,
            interaction: Interaction,
            event_type: str,
            event_date: str,
            event_time: str,
            description: str = "",
            ranked: bool = False
    ):
        """ Create an event help request and handle user interactions. """

        # Check if the time is in the correct format (HH:MM)
        if not re.match(r"^\d{1,2}:\d{2}$", event_time):
            await interaction.response.send_message("Please enter the time in HH:MM format.", ephemeral=True)
            return

        # Split the time into hour and minute and convert to integers
        hour, minute = map(int, event_time.split(':'))

        # Validate hour and minute
        if hour < 0 or hour > 23:
            await interaction.response.send_message("Invalid hour. Please enter a valid time (HH:MM, 24-hour format).", ephemeral=True)
            return

        if minute < 0 or minute > 59:
            await interaction.response.send_message("Invalid minute. Please enter a valid time (HH:MM, 24-hour format).", ephemeral=True)
            return

        # Adjust event time and date if necessary
        if event_time == "24:00":
            event_date = (datetime.strptime(event_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            event_time = "00:00"

        event_datetime_str = f"{event_date} {event_time}"
        event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

        if event_datetime <= datetime.now(timezone.utc):
            return await interaction.response.send_message("The event time must be in the future.", ephemeral=True)

        # Create and send the event embed with buttons
        event_timestamp = int(event_datetime.timestamp())
        embed_title = f"Help Me: {event_type}{' Ranked' if ranked else ''}"
        embed_description = (
            f"Event Date: <t:{event_timestamp}:d>\nEvent Time: <t:{event_timestamp}:t>\n\n"
            f"**Participants (Max 5):**\n• {interaction.user.mention}\n"
        )
        if description:
            embed_description = f"{description}\n\n" + embed_description

        embed = Embed(title=embed_title, description=embed_description, color=Color.blue())

        # Buttons for the event embed
        join_button = Button(label="Join", style=ButtonStyle.green)
        join_button.callback = self.join_event
        leave_button = Button(label="Leave", style=ButtonStyle.red)
        leave_button.callback = self.leave_event
        delete_button = Button(label="Delete Event", style=ButtonStyle.danger)
        delete_button.callback = self.delete_event

        view = View(timeout=None)
        view.add_item(join_button)
        view.add_item(leave_button)
        view.add_item(delete_button)

        reminder_channel = self.bot.get_channel(REMINDER_CHANNEL_ID)
        if reminder_channel:
            message = await reminder_channel.send(embed=embed, view=view)
            message_id = message.id

            bot_task = self.bot.loop.create_task(self.send_reminder(message_id, event_datetime))
            self.help_sessions[message_id] = {
                "embed": embed,
                "members": [interaction.user],
                "join_button": join_button,
                "leave_button": leave_button,
                "delete_button": delete_button,
                "initiator_id": interaction.user.id,
                "channel_id": REMINDER_CHANNEL_ID,
                "bot_task": bot_task,
            }
    
        await interaction.response.send_message("Event created successfully!", ephemeral=True)

    async def join_event(self, button_interaction: Interaction):
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

    async def leave_event(self, button_interaction: Interaction):
        message_id = button_interaction.message.id
        user_id = button_interaction.user.id
        session = self.help_sessions.get(message_id)
        if session:
            if user_id == session["initiator_id"]:
                await button_interaction.response.send_message(
                    "You cannot leave the event as you are the initiator.",
                    ephemeral=True,
                )
            elif button_interaction.user not in session['members']:
                await button_interaction.response.send_message("You are not part of this event.", ephemeral=True)
            else:
                session['members'].remove(button_interaction.user)
                session['embed'].description = session['embed'].description.replace(
                    f"• {button_interaction.user.mention}\n", "")
                await button_interaction.message.edit(embed=session['embed'])
                await button_interaction.response.defer()

    async def delete_event(self, button_interaction: Interaction):
        message_id = button_interaction.message.id
        if message_id in self.help_sessions:
            if button_interaction.user.id == self.help_sessions[message_id]["initiator_id"]:
                bot_task = self.help_sessions[message_id]['bot_task']
                del self.help_sessions[message_id]
                await button_interaction.message.delete()
                bot_task.cancel()
            else:
                await button_interaction.response.send_message(
                    "You cannot delete this event as you are not the initiator.",
                    ephemeral=True,
                )

    async def send_reminder(self, message_id, event_datetime):
        now_utc = datetime.now(timezone.utc)
        wait_time = (event_datetime - now_utc).total_seconds()
        await asyncio.sleep(wait_time)
        session = self.help_sessions.pop(message_id, None)
        if session:
            # go through each member of the session and if they have pm send them pm
            # otherwise tag them in reminder-channel
            channel_members = []
            pm_messages = []
            for member in session['members']:
                if await self.get_user_preference(member.id):
                    try:
                        pm_messages.append(
                            await member.send(f"Reminder: Event '{session['embed'].title}' is starting!")
                        )
                    except Forbidden:
                        logging.warning(f"Failed to send DM to {member.name}")
                        channel_members.append(member)
                    except Exception as e:
                        logging.error(f"Error sending DM to {member.name}: {e}")
                        channel_members.append(member)
                else:
                    channel_members.append(member)
            member_mentions = ' '.join(member.mention for member in channel_members)
            channel = self.bot.get_channel(session['channel_id'])
            if channel:
                reminder_msg = None
                if member_mentions:
                    reminder_msg = await channel.send(f"Event starting! {member_mentions}")
                # Delete the event and reminders after one hour
                await asyncio.sleep(3600)  # Wait for 1 hour after the event - 3600 seconds
                message = await channel.fetch_message(message_id)
                await message.delete()
                if reminder_msg:
                    await reminder_msg.delete()
                for pm_message in pm_messages:
                    await pm_message.delete()

    # New command for toggling direct message preferences
    @app_commands.command(name="pm", description="Toggle direct message notifications for events")
    async def toggle_pm(self, interaction: Interaction, is_pm: bool):
        await self.set_user_preference(interaction.user.id, is_pm)
        await interaction.response.send_message(
            f"Direct message notifications have been {'enabled' if is_pm else 'disabled'}.",
            ephemeral=True,
        )

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(HelpMe(bot))