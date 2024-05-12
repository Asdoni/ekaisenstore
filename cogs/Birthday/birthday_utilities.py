import re
from datetime import datetime
import discord
import calendar

class BirthdayUtilities:
    def __init__(self, db, bot=None):
        self.db = db
        self.bot = bot
        
    async def register_birthday(self, guild_id, user_id, birthday):
        day = birthday.day
        month = birthday.month
        year = birthday.year if birthday.year > 1 else 1

        existing = await self.db.fetchone("""
            SELECT user_id FROM birthdays WHERE user_id = $1 AND guild_id = $2
        """, user_id, guild_id)
        
        await self.db.execute("""
            INSERT INTO birthdays (guild_id, user_id, birth_day, birth_month, birth_year)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id, user_id) DO UPDATE
            SET birth_day = EXCLUDED.birth_day, birth_month = EXCLUDED.birth_month, birth_year = EXCLUDED.birth_year
        """, guild_id, user_id, day, month, year)

        formatted_birthday = birthday.strftime(f"%d/%m{'/%Y' if year > 1 else ''}")

        if existing:
            message = f"Birthday updated for <@{user_id}> - {formatted_birthday}."
        else:
            message = f"Birthday registered for <@{user_id}> - {formatted_birthday}."

        await self.update_birthday_list_embed(guild_id)

        return message
    
    @staticmethod
    def format_birthday(birthday_date, display_year):
        if display_year == 1:
            return birthday_date.strftime("%d/%m")
        else:
            return birthday_date.strftime(f"%d/%m/{display_year}")
    
    async def delete_birthday(self, guild_id, user_id):
        existing = await self.db.fetchone("""
            SELECT user_id FROM birthdays WHERE guild_id = $1 AND user_id = $2
        """, guild_id, user_id)
        if existing:
            await self.db.execute("""
                DELETE FROM birthdays WHERE guild_id = $1 AND user_id = $2
            """, guild_id, user_id)
            message = f"Birthday deleted for <@{user_id}>."
            
            await self.update_birthday_list_embed(guild_id)
        else:
            message = f"Birthday not set for <@{user_id}>."

        return message

    async def get_birthday(self, guild_id, user_id):
        result = await self.db.fetchone("""
            SELECT birth_day, birth_month, birth_year FROM birthdays WHERE guild_id = $1 AND user_id = $2
        """, guild_id, user_id)
        if result:
            birthday_data = {
                'day': result['birth_day'],
                'month': result['birth_month'],
                'year': result['birth_year'],
                'mention': f"<@{user_id}>"
            }
            return birthday_data
        else:
            print(f"No birthday found for user {user_id} in guild {guild_id}")
            return None
        
    @staticmethod
    def format_birthday_display(self, birthday_data):
        if birthday_data['birth_year'] > 1:
            return datetime(birthday_data['birth_year'], birthday_data['birth_month'], birthday_data['birth_day']).strftime("%d/%m/%Y")
        else:
            return datetime(1, birthday_data['birth_month'], birthday_data['birth_day']).strftime("%d/%m")

    async def get_birthdays(self, guild_id):
        try:
            results = await self.db.fetchall("""
                SELECT user_id, birth_day, birth_month, birth_year FROM birthdays WHERE guild_id = $1
            """, guild_id)
            print(f"Fetched birthday data: {results}")
            return results
        except Exception as e:
            print(f"Error fetching birthdays: {e}")
            return []

    @staticmethod
    def is_leap_year(year):
        return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)
    
    async def set_birthday_channel(self, guild_id, channel_id):
        old_channel_id = await self.get_birthday_channel(guild_id)
        if old_channel_id and old_channel_id != channel_id:
            old_channel = self.bot.get_guild(guild_id).get_channel(old_channel_id)
            if old_channel:
                message_id = await self.get_birthday_list_message_id(guild_id)
                if message_id:
                    try:
                        old_message = await old_channel.fetch_message(message_id)
                        await old_message.delete()
                    except discord.NotFound:
                        print("Old message not found, nothing to delete.")

        await self.db.execute("""
            INSERT INTO settings (guild_id, birthday_channel)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET birthday_channel = EXCLUDED.birthday_channel
        """, guild_id, channel_id)
        return f"Channel set/updated successfully: <#{channel_id}>."
    
    async def get_birthday_channel(self, guild_id):
        result = await self.db.fetchone("""
            SELECT birthday_channel FROM settings WHERE guild_id = $1
        """, guild_id)
        return result['birthday_channel'] if result else None
    
    async def delete_birthday_channel(self, guild_id):
        existing = await self.db.fetchone("""
            SELECT birthday_channel FROM settings WHERE guild_id = $1
        """, guild_id)
        if existing and existing['birthday_channel']:
            old_channel_id = existing['birthday_channel']
            old_channel = self.bot.get_guild(guild_id).get_channel(old_channel_id)
            if old_channel:
                message_id = await self.get_birthday_list_message_id(guild_id)
                if message_id:
                    try:
                        old_message = await old_channel.fetch_message(message_id)
                        await old_message.delete()
                    except discord.NotFound:
                        print("Old message not found, nothing to delete.")
            await self.db.execute("""
                UPDATE settings SET birthday_channel = NULL WHERE guild_id = $1
            """, guild_id)
            message = f"Channel <#{old_channel_id}> deleted."
        else:
            message = "Channel not existent or already unset."

        return message
        
    async def set_birthday_message(self, guild_id, message):
        existing = await self.db.fetchone("""
            SELECT birthday_message FROM settings WHERE guild_id = $1
        """, guild_id)
        if existing:
            await self.db.execute("""
                UPDATE settings SET birthday_message = $1 WHERE guild_id = $2
            """, message, guild_id)
            message = f"Birthday message updated\nMessage: {message}."
        else:
            await self.db.execute("""
                INSERT INTO settings (guild_id, birthday_message)
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE
                SET birthday_message = EXCLUDED.birthday_message
            """, guild_id, message)
            message = f"Birthday message registered.\nMessage: {message}."

        return message

    async def get_birthday_message(self, guild_id):
        result = await self.db.fetchone("""
            SELECT birthday_message FROM settings WHERE guild_id = $1
        """, guild_id)
        return result['birthday_message'] if result else None
    
    async def delete_birthday_message(self, guild_id):
        existing = await self.db.fetchone("""
            SELECT birthday_message FROM settings WHERE guild_id = $1
        """, guild_id)
        if existing and existing['birthday_message']:
            await self.db.execute("""
                UPDATE settings SET birthday_message = NULL WHERE guild_id = $1
            """, guild_id)
            message = f"Custom Message deleted."
        else:
            message = "Message not existent or already unset."

        return message
    
  
    async def set_birthday_role(self, guild_id, role_id):
        existing = await self.db.fetchone("""
            SELECT birthday_role_id FROM settings WHERE guild_id = $1
        """, guild_id)
        if existing:
            await self.db.execute("""
                INSERT INTO settings (guild_id, birthday_role_id)
                VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE
                SET birthday_role_id = EXCLUDED.birthday_role_id
            """, guild_id, role_id)
            message = f"Role updated to <@&{role_id}>."
        else:
            await self.db.execute("""
                INSERT INTO settings (guild_id, birthday_role_id)
                VALUES ($1, $2)
            """, guild_id, role_id)
            message = f"Role registered to <@&{role_id}>."

        return message
    
    async def get_birthday_role(self, guild_id):
        result = await self.db.fetchone("""
            SELECT birthday_role_id FROM settings WHERE guild_id = $1
        """, guild_id)
        return result['birthday_role_id'] if result else None

    # Not used
    async def delete_birthday_role(self, guild_id):
        existing = await self.db.fetchone("""
            SELECT birthday_role_id FROM settings WHERE guild_id = $1
        """, guild_id)
        if existing and existing['birthday_role_id']:
            await self.db.execute("""
                UPDATE settings SET birthday_role_id = NULL WHERE guild_id = $1
            """, guild_id) 
            message = "Role deleted."
        else:
            message = "Role not existent or already unset."

        return message
    
    # Not used
    async def get_all_guild_ids(self):
        result = await self.db.fetchall("SELECT DISTINCT guild_id FROM settings")
        return [row['guild_id'] for row in result]

    async def get_birthdays_on_date(self, guild_id, month, day):
        return await self.db.fetchall("""
            SELECT user_id FROM birthdays 
            WHERE guild_id = $1 AND birth_month = $2 AND birth_day = $3
        """, guild_id, month, day)
    
    async def upsert_record(self, table, conflict_columns, data):
        columns = ', '.join(data.keys())
        values = ', '.join(f"${i+1}" for i in range(len(data)))
        updates = ', '.join(f"{k} = EXCLUDED.{k}" for k in data.keys())
        conflict = ', '.join(conflict_columns)

        query = f"""
        INSERT INTO {table} ({columns})
        VALUES ({values})
        ON CONFLICT ({conflict}) DO UPDATE SET {updates}
        """
        await self.db.execute(query, *data.values())

    async def ensure_birthday_role(self, guild):
        existing_role_id = await self.get_birthday_role(guild.id)
        if existing_role_id:
            role = guild.get_role(existing_role_id)
            if role:
                return role

        role_name = "Birthday Celebrant"
        emoji_icon = "\U0001F382"
        try:
            if "ROLE_ICONS" in guild.features:
                role = await guild.create_role(name=role_name, reason="Highlight members on their birthday", unicode_emoji=emoji_icon)
            else:
                role = await guild.create_role(name=role_name, reason="Highlight members on their birthday")

            await self.set_birthday_role(guild.id, role.id)
            return role
        except Exception as e:
            print(f"Failed to create birthday role in {guild.name}: {str(e)}")
            return None

    @staticmethod
    def parse_birthday(birthday_input):
        print(f"Received input for parsing: {birthday_input}")

        birthday_input = birthday_input.strip().replace('/', '-')
        
        if not re.match(r"^\d{2}[-/]\d{2}([-/](\d{2}|\d{4}))?$", birthday_input):
            return None, "Invalid format. Please use DD/MM/YY, DD/MM/YYYY\nSeparator must be '-' or '/'."
        
        parts = birthday_input.split('-')
        day, month = int(parts[0]), int(parts[1])
        if len(parts) == 3:
            year = int(parts[2])
            if len(parts[2]) == 2:
                year += 2000 if year < 50 else 1900
        else:
            year = 1

        try:
            birthday_date = datetime(year, month, day)
        except ValueError:
            return None, "Invalid date. Please check the day and month."
        
        if birthday_date > datetime.now():
            return None, "Your birthday cannot be in the future or... Can it?"

        return birthday_date, None
    
    @staticmethod
    async def delete_message_on_timeout(bot, message):
        """Attempt to delete a message and handle potential exceptions."""
        if message:
            try:
                await message.delete()
                print("Message deleted successfully")
            except discord.NotFound:
                print("Message already deleted or not found")
            except discord.Forbidden:
                print("Bot does not have permission to delete the message")
            except Exception as e:
                print(f"Unexpected error when attempting to delete message: {e}")
        else:
            print("No message to delete or message reference not set")

    # Not used
    def create_basic_embed(title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Powered by EGirlzStore Bot ©")
        return embed
    
    async def get_guild_settings(self, guild_id):
        """Fetches the settings for a specific guild from the database."""
        return await self.db.fetchone("SELECT * FROM settings WHERE guild_id = $1", guild_id)

    async def update_birthday_list_message_id(self, guild_id, message_id):
        await self.db.execute("""
            UPDATE settings SET birthday_list_message_id = $2 WHERE guild_id = $1
        """, guild_id, message_id)

    async def update_birthday_list_embed(self, guild_id):
        try:
            channel_id = await self.get_birthday_channel(guild_id)
            if channel_id:
                channel = self.bot.get_guild(guild_id).get_channel(channel_id)
                if channel:
                    birthday_dict = await self.db.fetchall("""
                        SELECT user_id, birth_day, birth_month, birth_year
                        FROM birthdays
                        WHERE guild_id = $1
                    """, guild_id)
                    if isinstance(birthday_dict, list):
                        birthday_dict = await self.prepare_birthday_data(guild_id)
                    else:
                        birthday_dict = await self.prepare_birthday_data(guild_id)
                    embed = self.prepare_birthday_list_embed(channel, birthday_dict)

                    settings = await self.get_guild_settings(guild_id)
                    message_id = settings.get('birthday_list_message_id')
                    if message_id:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.edit(embed=embed)
                            print("Birthday list message updated.")
                        except discord.NotFound:
                            print("Birthday list message not found. Posting a new message.")
                            message = await channel.send(embed=embed)
                            await self.update_birthday_list_message_id(guild_id, message.id)
                    else:
                        message = await channel.send(embed=embed)
                        await self.update_birthday_list_message_id(guild_id, message.id)
                else:
                    print(f"Channel ID {channel_id} is not valid or the bot lacks permissions.")
            else:
                print("No channel set for birthday announcements.")
        except Exception as e:
            print(f"Error during update of birthday list: {e}")

    async def prepare_birthday_data(self, guild_id):
        guild = self.bot.get_guild(guild_id)
        birthdays = await self.db.fetchall("""
            SELECT user_id::text, birth_day, birth_month, birth_year FROM birthdays 
            WHERE guild_id = $1
        """, guild_id)

        birthday_dict = {}
        for birthday in birthdays:
            user_id = str(birthday['user_id'])
            user = guild.get_member(int(user_id))
            if not user:
                continue
            day, month, year = birthday['birth_day'], birthday['birth_month'], birthday['birth_year']

            month_name = calendar.month_name[month]
            if year > 1:
                formatted_birthday = f"{day:02d} {month_name} {year}"
            else:
                formatted_birthday = f"{day:02d} {month_name}"

            if month_name not in birthday_dict:
                birthday_dict[month_name] = []
            birthday_dict[month_name].append((day, f"{user.mention} {formatted_birthday}"))

        # Sort the birthdays within each month by day
        for month in birthday_dict:
            birthday_dict[month].sort(key=lambda x: x[0])
            birthday_dict[month] = [birthday[1] for birthday in birthday_dict[month]]

        return birthday_dict
    
    def prepare_birthday_list_embed(self, interaction, birthday_dict):
        embed = discord.Embed(title=f"🎂 Birthday List - {interaction.guild.name}", description="Here are the registered birthdays:", color=discord.Color.gold())
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        if birthday_dict:
            for month_name in sorted(birthday_dict.keys(), key=lambda x: datetime.strptime(x, "%B")):
                month_birthdays = "\n".join(birthday_dict[month_name])
                if month_birthdays:
                    embed.add_field(name=month_name, value=month_birthdays, inline=False)
        else:
            embed.description += "\n\nNo birthdays registered yet."

        return embed
    
    async def get_birthday_list_message_id(self, guild_id):
        result = await self.db.fetchone("""
            SELECT birthday_list_message_id FROM settings WHERE guild_id = $1
        """, guild_id)
        return result['birthday_list_message_id'] if result and result['birthday_list_message_id'] else None
    
    async def delete_birthday(self, guild_id, user_id):
        existing = await self.db.fetchone("""
            SELECT user_id FROM birthdays WHERE guild_id = $1 AND user_id = $2
        """, guild_id, user_id)
        if existing:
            await self.db.execute("""
                DELETE FROM birthdays WHERE guild_id = $1 AND user_id = $2
            """, guild_id, user_id)
            return f"Birthday deleted for user {user_id} in guild {guild_id}."
        else:
            return f"No birthday record found for user {user_id} in guild {guild_id}."
