import time
import random
import asyncio
import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

from bot import EGirlzStoreBot

ALLOWED_CHANNEL_ID = 1066425511401766982

class Javir(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.cooldowns = {}
        self.locks = {}    

    async def javir_reset(self, interaction: Interaction, user: User):
        # Reset user stats in the database
        await self.set_user_data(user.id, 0, 0, 0, 0, 0, 0)  # Resetting all values to 0

        # Send confirmation message
        await interaction.response.send_message(f"Stats for {user.display_name} have been reset.", ephemeral=True)

    async def simulate_upgrade(self, interaction, start_level, max_level, attempts, start_time, dolls=False):
        # Set success rates for each level range
        success_rates = ([0.50] * (100 - 20)) + ([0.40] * (110 - 100)) + ([0.30] * (120 - 110)) + ([0.20] * (130 - 120))

        successes = 0
        attempt_counts = []
        dolls_used_per_attempt = []

        last_check_time = time.time()
        for attempt in range(attempts):
            level = start_level
            attempt_count = 0
            dolls_used_this_attempt = 0

            while level < max_level:
                attempt_count += 1

                # Check if dolls are used and accumulate the count
                if dolls:
                    dolls_needed = int(str(level)[0])
                    dolls_used_this_attempt += dolls_needed

                # Calculate index for success rates, ensuring it's within the list's range
                index = max(0, min(level - 20, len(success_rates) - 1))  # Assuming levels start at 20

                if random.random() < success_rates[index]:
                    level += 1
                    if level == max_level:
                        successes += 1
                        break
                else:
                    # If not using dolls and level is not 20, 100, or 130, downgrade
                    if not dolls and level not in [20, 100, 130]:
                        level = max(20, level - 1)  # Ensuring level doesn't go below 20

                # Check progress every minute
#                current_time = time.time()
#                if current_time - last_check_time >= 60:
#                    elapsed_time = current_time - start_time
#                    progress = (attempt / attempts) * 100
#                    if attempt > 0 and attempts > 0:
#                        estimated_total_time = elapsed_time / (attempt / attempts)
#                        estimated_remaining_time = estimated_total_time - elapsed_time
#                        print(f"Progress: {progress:.2f}%, Estimated Remaining Time: {estimated_remaining_time/60:.2f} minutes")
#                    last_check_time = current_time

            attempt_counts.append(attempt_count)
            dolls_used_per_attempt.append(dolls_used_this_attempt)

        probability_to_reach_max = successes / attempts
        max_dolls_used = max(dolls_used_per_attempt) if dolls_used_per_attempt else 0
        min_dolls_used = min(dolls_used_per_attempt) if dolls_used_per_attempt else 0
        avg_dolls_used = sum(dolls_used_per_attempt) / len(dolls_used_per_attempt) if dolls_used_per_attempt else 0
        return probability_to_reach_max, attempt_counts, max_dolls_used, min_dolls_used, avg_dolls_used


    def format_value(self, value):
        if value < 5000:
            return str(value)
        elif value < 1000000:
            return str(int(value / 1000)) + 'k'
        else:
            return str(int(value / 1000000)) + 'm'

    def get_embed_with_thumbnail(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        embed.set_thumbnail(url="attachment://javir.png")
        return embed

    async def get_user_data(self, user_id):
        query = """
            SELECT current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak
            FROM javir_stats
            WHERE user_id = %s
        """
        result = await self.bot.db.fetchone(query, (user_id,))
        if result:
            return {
                "current_value": result[0], 
                "failures": result[1], 
                "successes": result[2], 
                "highest_level": result[3],
                "highest_success_streak": result[4],
                "longest_fail_streak": result[5]
            }
        else:
            return {
                "current_value": 0, 
                "failures": 0, 
                "successes": 0, 
                "highest_level": 0,
                "highest_success_streak": 0,
                "longest_fail_streak": 0
            }

    async def set_user_data(self, user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak):
        query = """
            INSERT INTO javir_stats (user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            current_value = VALUES(current_value),
            failures = VALUES(failures),
            successes = VALUES(successes),
            highest_level = VALUES(highest_level),
            highest_success_streak = VALUES(highest_success_streak),
            longest_fail_streak = VALUES(longest_fail_streak)
        """
        await self.bot.db.commit(query, (user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak))

    async def get_lock(self, user_id):
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()
        return self.locks[user_id]

    @app_commands.command(
        name="javir",
        description="Upgrade your items multiple times!"
    )
    @app_commands.describe(
        tries='How many times to try the upgrade. Use 5, 10, or 25.'
    )
    @app_commands.choices(tries=[
        app_commands.Choice(name="5", value=5),
        app_commands.Choice(name="10", value=10),
        app_commands.Choice(name="25", value=25),
        app_commands.Choice(name="50", value=50),
        app_commands.Choice(name="100", value=100),
    ])
    async def javir(self, interaction: Interaction, tries: int = 1):
        if interaction.channel.id != ALLOWED_CHANNEL_ID:
            await interaction.response.send_message(f"This command can only be used in <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
            return

        user_id = interaction.user.id
        lock = await self.get_lock(user_id)
        
        async with lock:
            user_data = await self.get_user_data(user_id)

            total_attempts_from_db = user_data["failures"] + user_data["successes"]
            stones = self.format_value(total_attempts_from_db)
            dmc = self.format_value(30 * total_attempts_from_db)
            territe = self.format_value(100 * total_attempts_from_db)
            gold = self.format_value(30 * total_attempts_from_db * 1000)

            if user_data["current_value"] >= 100:
                embed = self.get_embed_with_thumbnail(
                    "Javir Upgrade Results",
                    f"Congratulations {interaction.user.mention}! Your item is Maxed!",
                    discord.Color.blue()
                )
                embed.set_footer(text=f"Stones: {stones} | DMC: {dmc} | Territe: {territe} | Gold: {gold}\nTotal Attempts: {total_attempts_from_db} | Highest Level: {user_data['highest_level']}")
                file = discord.File('./cogs/NNK/javir.png', filename='javir.png')
                await interaction.response.send_message(file=file, embed=embed)
                return

            start_value = user_data["current_value"]
            descriptions = []
            total_successes = 0
            total_failures = 0
            current_success_streak = 0
            current_fail_streak = 0
            final_value = user_data["current_value"]
            initial_value = user_data["current_value"]
            final_value = initial_value 
            success_symbols = []

            for attempt in range(tries):
                attempts_used = attempt + 1

                if final_value == 100:
                    description = f"Congratulations {interaction.user.mention}! Your item is Maxed!"
                    embed_color = discord.Color.blue()
                    break

                success = random.choice([True, False])

                if success:
                    final_value += 1
                    current_success_streak += 1
                    current_fail_streak = 0
                    user_data["highest_success_streak"] = max(user_data["highest_success_streak"], current_success_streak)
                    success_symbols.append('✅')
                    total_successes += 1
                    description = f"✅ Success!\nYour item has been upgraded to {final_value}."
                else:
                    final_value = max(0, final_value - 1)
                    current_fail_streak += 1
                    current_success_streak = 0
                    user_data["longest_fail_streak"] = max(user_data["longest_fail_streak"], current_fail_streak)
                    success_symbols.append('❌')
                    total_failures += 1
                    description = f"❌ Failed!\nYour item has been downgraded to {final_value}."

                descriptions.append(description)

                if final_value >= 100:
                    break

                attempts_used = attempt + 1
            
            net_change = final_value - initial_value

            summary_line = f"{''.join(success_symbols)} → "
            if net_change > 0:
                summary_line += f"Congrats, +{net_change}"
            elif net_change < 0:
                summary_line += f"Unlucky, {net_change}"
            else:
                summary_line += "No change"

            if tries in [5, 10, 25]:
                descriptions.append(summary_line)

            if final_value > start_value:
                embed_color = discord.Color.green()
            elif final_value < start_value:
                embed_color = discord.Color.red()
            else:
                embed_color = discord.Color.yellow()

            if final_value > user_data["highest_level"]:
                user_data["highest_level"] = final_value

            await self.set_user_data(user_id, final_value, user_data["failures"] + total_failures, user_data["successes"] + total_successes, user_data["highest_level"], user_data["highest_success_streak"], user_data["longest_fail_streak"])

            updated_user_data = await self.get_user_data(user_id)
            total_attempts_from_db = updated_user_data["failures"] + updated_user_data["successes"]

            if tries >= 5:
                if final_value > start_value:
                    description = f"✅ Success!\nYour item has been upgraded from {start_value} to {final_value}.\nNumber of attempts: {attempts_used}\n\n{summary_line}"
                    embed_color = discord.Color.green()
                elif final_value < start_value:
                    description = f"❌ Failed!\nYour item has been downgraded from {start_value} to {final_value}.\nNumber of attempts: {attempts_used}\n\n{summary_line}"
                    embed_color = discord.Color.red()
                else:
                    description = f"⚠️ No change!\nYour item remains at {final_value}.\nNumber of attempts: {attempts_used}\n\n{summary_line}"
                    embed_color = discord.Color.yellow()
                descriptions = [description]

            else:
                if user_data["current_value"] > start_value:
                    embed_color = discord.Color.green()
                elif user_data["current_value"] < start_value:
                    embed_color = discord.Color.red()
                else:
                    embed_color = discord.Color.yellow()

        if final_value > start_value:
            embed_color = discord.Color.green()
        elif final_value < start_value:
            embed_color = discord.Color.red()
        else:
            embed_color = discord.Color.yellow()

        embed_description = "\n".join(descriptions)
        embed = self.get_embed_with_thumbnail("Javir Upgrade Results", embed_description, embed_color)
        embed.set_footer(text=f"Stones: {stones} | DMC: {dmc} | Territe: {territe} | Gold: {gold}\nTotal Attempts: {total_attempts_from_db} | Highest Level: {updated_user_data['highest_level']}")

        file = discord.File('./cogs/NNK/javir.png', filename='javir.png')
        await interaction.response.send_message(file=file, embed=embed)

    @app_commands.command(
        name="javirleaderboard",
        description="Show Javir leaderboard!"
    )
    @app_commands.choices(
        sort_by=[
            app_commands.Choice(name="Current Value", value="current_value"),
            app_commands.Choice(name="Success Rate", value="success_rate"),
            app_commands.Choice(name="Highest Level", value="highest_level"),
            app_commands.Choice(name="Highest Success Streak", value="highest_success_streak"),
            app_commands.Choice(name="Longest Fail Streak", value="longest_fail_streak")
        ]
    )
    async def leaderboard(self, interaction: Interaction, sort_by: app_commands.Choice[str] = None):
        await interaction.response.defer()

        if sort_by is None or sort_by.value == "current_value":
            query = "SELECT user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak FROM javir_stats ORDER BY current_value DESC, successes DESC"
        elif sort_by.value == "success_rate":
            query = "SELECT user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak FROM javir_stats ORDER BY (successes / (failures + successes)) DESC, successes DESC"
        elif sort_by.value == "highest_level":
            query = "SELECT user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak FROM javir_stats ORDER BY highest_level DESC, successes DESC"
        elif sort_by.value == "highest_success_streak":
            query = "SELECT user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak FROM javir_stats ORDER BY highest_success_streak DESC, successes DESC"
        elif sort_by.value == "longest_fail_streak":
            query = "SELECT user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak FROM javir_stats ORDER BY longest_fail_streak DESC, failures DESC"

        results = await self.bot.db.fetchall(query)

        embed = self.get_embed_with_thumbnail("Javir Leaderboard", "", random.randint(0, 0xFFFFFF))

        for idx, (user_id, current_value, failures, successes, highest_level, highest_success_streak, longest_fail_streak) in enumerate(results, 1):
            user = await self.bot.fetch_user(user_id)
            user_name = user.display_name
            success_rate = (successes / (failures + successes)) * 100 if (failures + successes) != 0 else 0

            embed.add_field(
                name=f"{idx}. {user_name}",
                value=(
                    f"Item Value: {current_value}\n"
                    f"Highest Level: {highest_level}\n"
                    f"Successes: {successes} | Failures: {failures}\n"
                    f"Success Rate: {success_rate:.2f}%\n"
                    f"Highest Success Streak: {highest_success_streak}\n"
                    f"Longest Fail Streak: {longest_fail_streak}"
                ),
                inline=False
            )

        file = discord.File('./cogs/NNK/javir.png', filename='javir.png')
        await interaction.followup.send(file=file, embed=embed)


    @app_commands.command(
        name="javirrank",
        description="Show your own or another user's Javir stats!"
    )
    @app_commands.describe(
        user="The user whose Javir stats you want to see. Leave empty to see your own stats."
    )
    async def rank(self, interaction: Interaction, user: User = None):
        if user is None:
            user = interaction.user

        user_id = user.id
        user_data = await self.get_user_data(user_id)
        user_name = user.display_name

        success_rate = (user_data['successes'] / (user_data['failures'] + user_data['successes'])) * 100 if (user_data['failures'] + user_data['successes']) != 0 else 0

        embed_description = (
            f"Item Value: {user_data['current_value']}\n"
            f"Highest Level: {user_data['highest_level']}\n"
            f"Successes: {user_data['successes']} | Failures: {user_data['failures']}\n"
            f"Success Rate: {success_rate:.2f}%\n"
            f"Highest Success Streak: {user_data['highest_success_streak']}\n"
            f"Longest Fail Streak: {user_data['longest_fail_streak']}"
        )
        embed = self.get_embed_with_thumbnail(f"{user_name}'s Javir Stats", embed_description, random.randint(0, 0xFFFFFF))

        file = discord.File('./cogs/NNK/javir.png', filename='javir.png')
        await interaction.response.send_message(file=file, embed=embed)


    @app_commands.command(
        name="javirupgrade",
        description="Simulate an item upgrade from one level to another."
    )
    @app_commands.describe(
        from_level='The starting level of the item.',
        to_level='The level you want to upgrade the item to.',
        simulations='The number of simulations to run.',
        dolls='Set to true to prevent downgrading on failure.'
    )
    @app_commands.choices(
        simulations=[
            app_commands.Choice(name="1", value=1),
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="100", value=100),
            app_commands.Choice(name="500", value=500),
            app_commands.Choice(name="1000", value=1000),
            app_commands.Choice(name="10000", value=10000),
        ]
    )
    async def javir_upgrade(self, interaction: Interaction, from_level: int, to_level: int, simulations: int = 100, dolls: bool = False):
        await interaction.response.defer()

        
        # Check if 'from_level' is in the correct range
        if not 20 <= from_level <= 129:
            await interaction.followup.send("Invalid 'from' level. It must be between 20 and 129.", ephemeral=True)
            return

        # Check if 'to_level' is in the correct range
        if not 21 <= to_level <= 130:
            await interaction.followup.send("Invalid 'to' level. It must be between 21 and 130.", ephemeral=True)
            return

        # Check if 'from_level' is less than 'to_level'
        if from_level >= to_level:
            await interaction.followup.send("Invalid levels. The 'from' level must be lower than the 'to' level.", ephemeral=True)
            return
        # Check if dolls is False and to_level is greater than 100
        if to_level > 100:
            await interaction.followup.send("Currently, the 'to' level cannot exceed 100.", ephemeral=True)
            return

        # Check if dolls is False and to_level is greater than 100
        #if not dolls and to_level > 100:
        #    await interaction.followup.send("Invalid 'to' level. When not using dolls, the 'to' level cannot exceed 100.", ephemeral=True)
        #    return

        # Start timing
        start_time = time.time()

        # Run the simulation
        probability_to_reach_max, attempt_counts, max_dolls_used, min_dolls_used, avg_dolls_used = await self.simulate_upgrade(interaction, from_level, to_level, simulations, start_time, dolls=dolls)
        
        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        formatted_total_time = "{:.2f}".format(total_time)

        # Sorting and formatting
        attempt_counts_sorted = sorted(attempt_counts)
        formatted_avg_attempts = "{:,.2f}".format(sum(attempt_counts) / len(attempt_counts))
        
        # Formatting the embed description
        embed_description = (
            f"Probability to reach +{to_level} from +{from_level}: {probability_to_reach_max:.2%}\n"
            f"Average number of attempts to reach +{to_level} from +{from_level}: {formatted_avg_attempts}\n"
            f"Total calculation time: {formatted_total_time} seconds\n"
        )

        # Include the doll usage information in the description if dolls were used
        if dolls:
            embed_description += (
                f"\nMax dolls used in a single attempt: {max_dolls_used}"
                f"\nMin dolls used in a single attempt: {min_dolls_used}"
                f"\nAverage dolls used per attempt: {avg_dolls_used:.2f}"
            )

        embed = self.get_embed_with_thumbnail(
            "Javir Upgrade Simulation Results",
            embed_description,
            discord.Color.blue()
        )

        # Add the top 10 highest and lowest attempt counts as fields in the embed
        embed.add_field(
            name="Top 10 Highest Attempt Counts",
            value=", ".join(map(str, attempt_counts_sorted[-10:])),
            inline=False
        )
        embed.add_field(
            name="Top 10 Lowest Attempt Counts",
            value=", ".join(map(str, attempt_counts_sorted[:10])),
            inline=False
        )

        # Calculate resources based on the average number of attempts
        avg_attempts = sum(attempt_counts) / len(attempt_counts)
        stones = self.format_value(avg_attempts)
        dmc = self.format_value(30 * avg_attempts)
        territe = self.format_value(100 * avg_attempts)
        gold = self.format_value(30 * avg_attempts * 1000)

        # Add resource information to the embed footer
        embed.set_footer(text=f"Stones: {stones} | DMC: {dmc} | Territe: {territe} | Gold: {gold}")

        file = discord.File('./cogs/NNK/javir.png', filename='javir.png')
        await interaction.followup.send(file=file, embed=embed)
    

    @app_commands.command(
        name="javirreset",
        description="Reset a user's Javir stats."
    )
    @app_commands.describe(
        user="The user whose Javir stats you want to reset."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def javir_reset(self, interaction: Interaction, user: User):
        # Check if the user invoking the command has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Reset user stats in the database
        await self.set_user_data(user.id, 0, 0, 0, 0, 0, 0)  # Resetting all values to 0

        # Send a confirmation message
        await interaction.response.send_message(f"Stats for {user.display_name} have been reset.", ephemeral=True)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Javir(bot))