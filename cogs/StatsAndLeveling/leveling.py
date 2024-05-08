import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
import hashlib

from bot import EGirlzStoreBot

class LevelingSystem(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.milestones = {
            1: "Hatchling",
            5: "Explorer",
            10: "Adventurer",
            20: "Knight",
            30: "Wizard",
            40: "Champion",
            50: "Dragon Slayer",
            60: "Legendary Hero",
            70: "Dimensional Traveler",
            80: "Galactic Guardian",
            90: "Timeless Master",
            100: "Celestial Sovereign"
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        message_content_hash = hashlib.sha256(message.content.encode('utf-8')).hexdigest()

        guild_setting = await self.bot.db.fetchone(
            "SELECT level_up_channel_id FROM guild_settings WHERE guild_id = $1", message.guild.id
        )
        level_up_channel_id = guild_setting['level_up_channel_id'] if guild_setting else None

        if level_up_channel_id:
            level_up_channel = self.bot.get_channel(level_up_channel_id)
            if not level_up_channel or not level_up_channel.permissions_for(message.guild.me).send_messages:
                level_up_channel = message.channel
        else:
            level_up_channel = message.channel

        user_info = await self.bot.db.fetchone(
            "SELECT xp, level, EXTRACT(EPOCH FROM (NOW() - last_message)) AS cooldown, last_message_hash FROM user_xp_levels WHERE user_id = $1 AND guild_id = $2",
            message.author.id, message.guild.id
        )
        cooldown = user_info['cooldown'] if user_info else None
        last_message_hash = user_info['last_message_hash'] if user_info else None

        if not user_info or (cooldown >= 10 and last_message_hash != message_content_hash):
            new_xp = user_info['xp'] + 5 if user_info else 5
            new_level = int((new_xp / 100) ** (1/1.5))

            await self.bot.db.execute(
                """
                INSERT INTO user_xp_levels (user_id, guild_id, xp, level, last_message, last_message_hash)
                VALUES ($1, $2, $3, $4, NOW(), $5)
                ON CONFLICT (user_id, guild_id)
                DO UPDATE SET xp = $3, level = $4, last_message = NOW(), last_message_hash = $5
                """,
                message.author.id, message.guild.id, new_xp, new_level, message_content_hash
            )
            
            if new_level > (user_info['level'] if user_info else 0):
                embed = discord.Embed(title="🎉 Level Up! 🎉", description=f"Congratulations {message.author.mention}, you've reached level **{new_level}**!", color=discord.Color.green())
                embed.set_thumbnail(url=message.author.display_avatar.url)
                embed.set_footer(text="Keep chatting to level up!", icon_url=self.bot.user.display_avatar.url)
                await level_up_channel.send(embed=embed)

                applicable_milestone_roles = {level: role_name for level, role_name in self.milestones.items() if level <= new_level}
                highest_milestone_level = max(applicable_milestone_roles.keys())
                new_milestone_role_name = applicable_milestone_roles[highest_milestone_level]
                new_milestone_role = get(message.guild.roles, name=new_milestone_role_name)

                milestone_role_names = set(self.milestones.values())
                for role in message.author.roles:
                    if role.name in milestone_role_names and role.name != new_milestone_role_name:
                        await message.author.remove_roles(role, reason="Level up - updating milestone role")
                if new_milestone_role and new_milestone_role not in message.author.roles:
                    await message.author.add_roles(new_milestone_role, reason="Level up - adding new milestone role")

                if new_level == highest_milestone_level:
                    custom_announcement = discord.Embed(title=f"🌟 Milestone Achieved! 🌟", description=f"Wow, {message.author.mention}! You've achieved the **{new_milestone_role_name}** role by reaching level **{new_level}**!", color=discord.Color.gold())
                    custom_announcement.set_thumbnail(url=message.author.display_avatar.url)
                    custom_announcement.set_footer(text="Next milestone awaits!", icon_url=self.bot.user.display_avatar.url)
                    await level_up_channel.send(embed=custom_announcement)


    async def on_member_remove(self, member):
        sql = """
        DELETE FROM user_xp_levels
        WHERE user_id = $1;
        """

        try:
            await self.bot.db.execute(sql, member.id)
            print(f"Successfully deleted stats for user {member} (ID: {member.id})")
        except Exception as e:
            print(f"Failed to delete stats for user {member} (ID: {member.id}): {e}")

    @app_commands.command(name="milestones", description="Displays all the leveling milestones.")
    async def milestones_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎯 Leveling Milestones 🎯", description="Here are the milestones you can achieve by leveling up!\n\n", color=discord.Color.purple())
        formula_description = "**Level Calculation Formula:** `Level = int((XP / 100) ** (1/1.5))`\n\n" \
                            "This means you level up by gaining XP, and each level requires progressively more XP. " \
                            "For example, reaching Level 1 requires 100 XP, Level 2 requires approximately 259 XP in total, and so on."
        embed.add_field(name="How Levels Are Calculated", value=formula_description, inline=False)

        for level, role_name in self.milestones.items():
            embed.add_field(name=f"Level {level}", value=f"Role: **{role_name}**", inline=False)

        embed.set_footer(text="Keep engaging to unlock these milestones!", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setlevelchannel", description="Sets the channel for level-up announcements.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_level_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            await self.bot.db.execute(
                "INSERT INTO guild_settings (guild_id, level_up_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET level_up_channel_id = $2",
                interaction.guild_id, channel.id
            )
            await interaction.response.send_message(f"Level-up announcements will now be sent to {channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to set level-up channel: {e}", ephemeral=True)

    @app_commands.command(name="unsetlevelchannel", description="Removes the specific channel for level-up announcements, reverting to the default behavior.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def unset_level_channel(self, interaction: discord.Interaction):
        try:
            await self.bot.db.execute(
                "UPDATE guild_settings SET level_up_channel_id = NULL WHERE guild_id = $1",
                interaction.guild_id
            )
            await interaction.response.send_message("Level-up announcements will now be sent to the channel where the message is posted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unset level-up channel: {e}", ephemeral=True)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(LevelingSystem(bot))
