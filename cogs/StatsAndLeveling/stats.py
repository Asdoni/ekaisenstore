import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord import TextChannel, VoiceChannel, Thread
import datetime
import calendar

from bot import EGirlzStoreBot

def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]

class StatsBot(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.daily_reset.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        channel_id = message.channel.id
        guild_id = message.guild.id 
        day_of_month = message.created_at.day
        column_name = f"day_{day_of_month}_count"
        
        sql = f"""
        INSERT INTO user_stats (user_id, channel_id, guild_id, total_messages, {column_name}, last_reset)
        VALUES ($1, $2, $3, 1, 1, CURRENT_DATE)
        ON CONFLICT (user_id, channel_id)
        DO UPDATE SET 
            total_messages = user_stats.total_messages + 1,
            {column_name} = user_stats.{column_name} + 1,
            last_reset = CURRENT_DATE;
        """
        await self.bot.db.execute(sql, user_id, channel_id, guild_id)

    @tasks.loop(time=datetime.time(hour=0, minute=1))
    async def daily_reset(self):
        today = datetime.datetime.now().day
        for day in range(1, 32):
            reset_column_name = f"day_{day}_count"
            if day == today:
                sql = f"UPDATE user_stats SET {reset_column_name} = 0;"
                await self.bot.db.execute(sql)

    @app_commands.command(name="channel_stats", description="Get stats for a specific channel")
    @app_commands.choices(timeframe=[
        app_commands.Choice(name="1 Day", value="1 day"),
        app_commands.Choice(name="3 Days", value="3 days"),
        app_commands.Choice(name="1 Week", value="7 days"),
        app_commands.Choice(name="1 Month", value="30 days"),
        app_commands.Choice(name="All", value="all")
    ])
    async def channel_stats(self, interaction: discord.Interaction, channel: TextChannel | VoiceChannel | Thread = None, timeframe: app_commands.Choice[str] = None):
        now = datetime.datetime.now(datetime.timezone.utc)
        target_channel = channel or interaction.channel
        
        display_timeframes = {
            "1 day": "1 Day",
            "3 days": "3 Days",
            "7 days": "1 Week",
            "30 days": "1 Month",
            "all": "All"
        }
        timeframe_value = timeframe.value if timeframe else "all"
        timeframe_display = display_timeframes.get(timeframe_value, "All Time")

        if timeframe_value == "all":
            total_messages_query = """
            SELECT SUM(total_messages) AS total
            FROM user_stats
            WHERE channel_id = $1;
            """
            top_users_query = """
            SELECT user_id, SUM(total_messages) AS total_messages
            FROM user_stats
            WHERE channel_id = $1
            GROUP BY user_id
            ORDER BY total_messages DESC
            LIMIT 3;
            """
            total_messages_result = await self.bot.db.fetchone(total_messages_query, target_channel.id)
            total_messages = total_messages_result['total'] if total_messages_result else 0
            top_users_result = await self.bot.db.fetchall(top_users_query, target_channel.id)

            leaderboard = "\n".join([f"{idx + 1}. <@{row['user_id']}> - {row['total_messages']} messages" for idx, row in enumerate(top_users_result)]) if top_users_result else "No data available."

            embed = discord.Embed(title="Channel Stats", color=discord.Color.blue())
            embed.add_field(name=f"Total Messages for {target_channel.mention}", value=str(total_messages), inline=False)
            embed.add_field(name="Top 3 Users", value=leaderboard, inline=False)
            embed.set_thumbnail(url=target_channel.guild.icon.url)
            embed.set_footer(text=f"Timeframe: {timeframe_display} | 📊 Powered by EGirlzStore Bot")
        else:
            days_to_include = 30 if timeframe_value == "1 Month" else int(timeframe_value.split()[0])
            days_columns = []
            for i in range(days_to_include):
                day_to_check = (now - datetime.timedelta(days=i)).day
                days_columns.append(f"day_{day_to_check}_count")
            column_sum_sql = " + ".join(days_columns)

            total_messages_query = f"""
            SELECT SUM({column_sum_sql}) AS total
            FROM user_stats
            WHERE channel_id = $1 AND last_reset >= (CURRENT_DATE - INTERVAL '{days_to_include} days');
            """
            top_users_query = f"""
            SELECT user_id, SUM({column_sum_sql}) AS total_messages
            FROM user_stats
            WHERE channel_id = $1 AND last_reset >= (CURRENT_DATE - INTERVAL '{days_to_include} days')
            GROUP BY user_id
            ORDER BY total_messages DESC
            LIMIT 3;
            """

            top_users_result = await self.bot.db.fetchall(top_users_query, target_channel.id)

            leaderboard = "\n".join([f"{idx + 1}. <@{row['user_id']}> - {row['total_messages']} messages" for idx, row in enumerate(top_users_result)]) if top_users_result else "No data available."

            total_messages_result = await self.bot.db.fetchone(total_messages_query, target_channel.id)
            total_messages = total_messages_result['total'] if total_messages_result else 0

            embed = discord.Embed(title="Channel Stats", color=discord.Color.blue())
            embed.add_field(name=f"Total Messages for {channel.mention}", value=str(total_messages), inline=False)
            embed.add_field(name="Top 3 Users", value=leaderboard, inline=False)
            embed.set_thumbnail(url=channel.guild.icon.url)
            embed.set_footer(text=f"Timeframe: {timeframe_display} | 📊 Powered by EGirlzStore Bot")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="member_stats", description="Get stats for a specific member")
    @app_commands.choices(timeframe=[
        app_commands.Choice(name="1 Day", value="1 day"),
        app_commands.Choice(name="3 Days", value="3 days"),
        app_commands.Choice(name="1 Week", value="7 days"),
        app_commands.Choice(name="1 Month", value="30 days"),
        app_commands.Choice(name="All", value="all")
    ])
    async def member_stats(self, interaction: discord.Interaction, member: discord.Member, timeframe: app_commands.Choice[str] = None):
        now = datetime.datetime.now(datetime.timezone.utc)
        display_timeframes = {
            "1 day": "1 Day",
            "3 days": "3 Days",
            "7 days": "1 Week",
            "30 days": "1 Month",
            "all": "All Time"
        }
        timeframe_value = timeframe.value if timeframe else "all"
        timeframe_display = display_timeframes.get(timeframe_value, "All Time")

        embed = discord.Embed(color=discord.Color.blue())
        if member.bot:
            embed.title = "Bot Stats 🤖"
            embed.description = f"{member.display_name} is a bot, and this is a bot's world."
            embed.color = 0x7289DA
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="🤖 Bots have different metrics | 📊 Powered by EGirlzStore Bot")
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return

        days_to_include = None
        if timeframe_value != "all":
            days_to_include = 30 if timeframe_value == "1 Month" else int(timeframe_value.split()[0])

        days_columns = [f"day_{(now - datetime.timedelta(days=i)).day}_count" for i in range(days_to_include)] if days_to_include else ["total_messages"]
        column_sum_sql = " + ".join(days_columns) if days_columns else "total_messages"
        interval_condition = f"AND last_reset >= (CURRENT_DATE - INTERVAL '{days_to_include} days')" if days_to_include else ""

        total_messages_query = f"""
        SELECT SUM({column_sum_sql}) AS total_messages
        FROM user_stats
        WHERE user_id = $1 AND guild_id = $2 {interval_condition};
        """
        total_messages_result = await self.bot.db.fetchone(total_messages_query, member.id, interaction.guild.id)
        total_messages = total_messages_result['total_messages'] if total_messages_result else 0

        xp_rank_query = f"""
        SELECT COUNT(*) + 1 AS rank
        FROM user_xp_levels
        WHERE xp > (
            SELECT xp FROM user_xp_levels WHERE user_id = $1 AND guild_id = $2
        ) AND guild_id = $2;
        """
        xp_rank_result = await self.bot.db.fetchone(xp_rank_query, member.id, interaction.guild.id)
        xp_rank = xp_rank_result['rank'] if xp_rank_result else "N/A"

        xp_and_level_query = f"""
        SELECT xp, level
        FROM user_xp_levels
        WHERE user_id = $1 AND guild_id = $2;
        """
        xp_and_level_result = await self.bot.db.fetchone(xp_and_level_query, member.id, interaction.guild.id)
        total_xp = xp_and_level_result['xp'] if xp_and_level_result and timeframe_value == "all" else None
        level = xp_and_level_result['level'] if xp_and_level_result else None

        top_channels_query = f"""
        SELECT channel_id, SUM({column_sum_sql}) AS messages
        FROM user_stats
        WHERE user_id = $1 AND guild_id = $2 {interval_condition}
        GROUP BY channel_id
        ORDER BY messages DESC
        LIMIT 3;
        """
        top_channels_result = await self.bot.db.fetchall(top_channels_query, member.id, interaction.guild.id)
        top_channels_display = "\n".join([f"<#{row['channel_id']}> - {row['messages']} messages" for row in top_channels_result]) if top_channels_result else "No data available."

        embed.title = "Member Stats"
        embed.description = f"Info for {member.mention}\n**Total Messages:** {total_messages}\n**Level:** {level if level is not None else 'N/A'}\n**XP Rank:** {xp_rank}"
        if total_xp is not None:
            embed.description += f"\n**Total XP:** {total_xp}"
        embed.add_field(name="Top 3 Channels", value=top_channels_display, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Timeframe: {timeframe_display} | 📊 Powered by EGirlzStore Bot")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Get the top users in the server")
    @app_commands.choices(timeframe=[
        app_commands.Choice(name="1 Day", value="1 day"),
        app_commands.Choice(name="3 Days", value="3 days"),
        app_commands.Choice(name="1 Week", value="7 days"),
        app_commands.Choice(name="1 Month", value="30 days"),
        app_commands.Choice(name="All", value="all")
    ])
    async def leaderboard(self, interaction: discord.Interaction, timeframe: str = "all"):
        now = datetime.datetime.now(datetime.timezone.utc)
        timeframe_value = timeframe 

        display_timeframes = {
            "1 day": "1 Day",
            "3 days": "3 Days",
            "7 days": "1 Week",
            "30 days": "1 Month",
            "all": "All Time"
        }

        timeframe_display = display_timeframes.get(timeframe_value, "All Time")

        if timeframe_value != "all":
            if timeframe_value == "1 Month":
                days_to_include = days_in_month(now.year, now.month)
            else:
                days_to_include = int(timeframe_value.split()[0])
        else:
            days_to_include = None

        if days_to_include:
            days_columns = [f"day_{(now - datetime.timedelta(days=i)).day}_count" for i in range(days_to_include)]
            column_sum_sql = " + ".join(days_columns)
            timeframe_condition = f"AND last_reset >= (CURRENT_DATE - INTERVAL '{days_to_include} days')"
            stats_field = f"SUM({column_sum_sql}) AS total_messages"
        else:
            timeframe_condition = ""
            stats_field = "SUM(user_stats.total_messages) AS total_messages, user_xp_levels.level AS level, user_xp_levels.xp AS xp"

        query = f"""
            SELECT user_stats.user_id, {stats_field}, COALESCE(user_xp_levels.level, 0) AS level, COALESCE(user_xp_levels.xp, 0) AS xp
            FROM user_stats
            LEFT JOIN user_xp_levels ON user_stats.user_id = user_xp_levels.user_id AND user_stats.guild_id = user_xp_levels.guild_id
            WHERE user_stats.guild_id = $1 {timeframe_condition}
            GROUP BY user_stats.user_id, user_xp_levels.level, user_xp_levels.xp
            ORDER BY user_xp_levels.xp DESC
            LIMIT 10;
        """

        top_users = await self.bot.db.fetchall(query, interaction.guild_id)

        description_lines = []
        for idx, user in enumerate(top_users):
            line = f"{idx+1}. <@{user['user_id']}> - {user['total_messages']} Messages\n**Level:** {user.get('level', 'N/A')} | **XP:** {user.get('xp', 'N/A')}"
            description_lines.append(line)
        description = "\n".join(description_lines) if description_lines else "No data available."

        embed = discord.Embed(title="🏆 Leaderboard 🏆", description=description, color=discord.Color.gold())
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"Timeframe: {timeframe_display} | 📊 Powered by EGirlzStore Bot")

        await interaction.response.send_message(embed=embed)

    @daily_reset.before_loop
    async def before_resets(self):
        await self.bot.wait_until_ready()

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(StatsBot(bot))
