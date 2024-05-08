import calendar

import discord
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot

class InfoCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="info",
        description="Get information about a user"
    )
    async def info(self, interaction: discord.Interaction, user: discord.Member = None):
        if not user:
            user = interaction.user

        joined_timestamp = calendar.timegm(user.joined_at.utctimetuple())
        created_timestamp = calendar.timegm(user.created_at.utctimetuple())

        roles = [f"<@&{role.id}>" for role in user.roles if role != interaction.guild.default_role]
        roles_str = ", ".join(roles)

        embed = discord.Embed(title=f"Member Information: {user.name}", color=discord.Color.blue())
        user_info_value = (
            f"Username: {user.display_name}\n"
            f"ID: {user.id}"
        )
        embed.add_field(name="User Info", value=user_info_value, inline=False)
        embed.add_field(
            name="Joined Server",
            value=f"<t:{joined_timestamp}:F> (<t:{joined_timestamp}:R>)",
            inline=False,
        )
        embed.add_field(
            name="Account Created",
            value=f"<t:{created_timestamp}:F> (<t:{created_timestamp}:R>)",
            inline=False,
        )

        max_length = 1024
        while len(roles_str) > 0:
            if len(roles_str) > max_length:
                split_index = roles_str.rfind(',', 0, max_length)
                value = roles_str[:split_index]
                roles_str = roles_str[split_index + 1:].strip()
            else:
                value = roles_str
                roles_str = ""

            field_name = "Roles (continued)" if "Roles (continued)" in [f.name for f in embed.fields] else "Roles"
            embed.add_field(name=field_name, value=value, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(InfoCog(bot))
