import discord
from discord import app_commands
from discord.ext import commands
import requests
import aiomysql
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import random
import logging

# Configure logging at the beginning of your script
logging.basicConfig(filename='myapp.log', level=logging.INFO)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
}

class CouponCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.executor = ThreadPoolExecutor()

    async def db_execute(self, query, params=None):
        async with aiomysql.create_pool(**DB_CONFIG) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
                    return await cursor.fetchall()

    def send_coupon_rewards(self, code, pid_ids):
        error = False
        error_messages = {}
        for pid in pid_ids:
            params = {"gameCode": "enngb", "couponCode": code, "pid": pid}
            response = requests.post('https://coupon.netmarble.com/api/coupon', json=params)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                if data['errorCode'] != 200:  # If errorCode is not 200, it's an error
                    error = True
                    if data['errorCode'] == 24002:
                        error_messages[pid] = "Invalid coupon code."
                    elif data['errorCode'] == 24004:
                        error_messages[pid] = "Coupon code has already been used."
                    elif data['errorCode'] == 21002:
                        error_messages[pid] = "Invalid PID."
                    elif data['errorCode'] == 24001:
                        error_messages[
                            pid] = "You have failed to enter the coupon number 10 times in a row. You can try again in 1 hour."
                    elif data['errorCode'] == 24003:
                        error_messages[pid] = "Code is expired."
                    else:
                        error_messages[pid] = "Unknown error."
            else:
                error = True
                error_messages[pid] = f"Error with status code: {response.status_code}"

        return error, error_messages

    @app_commands.command(
        name="pid",
        description="Set your PID in the database"
    )
    async def set_pid(self, interaction: discord.Interaction, set: str):
        await self.db_execute(
            """
            INSERT INTO user_pids (user_id, pid) VALUES (%s, %s) AS new_values
            ON DUPLICATE KEY UPDATE pid = new_values.pid
            """,
            (interaction.user.id, set)
        )
        await interaction.response.send_message(f"PID set to {set} for {interaction.user.mention}", ephemeral=True)


    @app_commands.command(
        name="redeem",
        description="Send coupon rewards to all registered PID's"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def redeem_coupon_code(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer(ephemeral=False)

        res = await self.db_execute('SELECT user_id, pid FROM user_pids')
        pid_to_user_id = {row[1]: row[0] for row in res}

        loop = asyncio.get_event_loop()
        error, pid_errors = await loop.run_in_executor(self.executor, self.send_coupon_rewards, code,
                                                    pid_to_user_id.keys())

        embeds = []
        current_embed = discord.Embed(title="Redeem Code Results", description=f"Redeem Code: `{code}`",
                                    color=random.randint(0, 0xFFFFFF))
        embeds.append(current_embed)
        user_list_value = ""

        for pid, user_id in pid_to_user_id.items():
            user_status = pid_errors.get(pid, "Code Redeemed")
            new_entry = f"<@{user_id}>: {'🟥 ' + user_status if user_status != 'Code Redeemed' else '🟩 Code Redeemed'}\n"

            if len(user_list_value) + len(new_entry) > 1024:
                current_embed.add_field(name="User List", value=user_list_value, inline=False)
                current_embed = discord.Embed(title="Redeem Code Results (continued)", color=random.randint(0, 0xFFFFFF))
                embeds.append(current_embed)
                user_list_value = new_entry  # Start with the new entry in the new embed
            else:
                user_list_value += new_entry

        # Add remaining users to the last embed
        if user_list_value:
            current_embed.add_field(name="User List (continued)", value=user_list_value, inline=False)

        # Send all embeds
        for embed in embeds:
            embed.set_footer(text="Redeem operation completed.")
            await interaction.followup.send(embed=embed)

            
async def setup(bot):
    await bot.add_cog(CouponCog(bot))
