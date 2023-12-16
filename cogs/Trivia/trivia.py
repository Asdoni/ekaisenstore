import asyncio
import html
import random

import discord
import requests
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

# Define categories and corresponding IDs
from bot import EGirlzStoreBot

CATEGORIES = [
    ("All categories", 0),
    ("General Knowledge", 9),
    ("Entertainment: Books", 10),
    ("Entertainment: Film", 11),
    ("Entertainment: Music", 12),
    ("Entertainment: Musicals & Theatres", 13),
    ("Entertainment: Television", 14),
    ("Entertainment: Video Games", 15),
    ("Entertainment: Board Games", 16),
    ("Science & Nature", 17),
    ("Science: Computers", 18),
    ("Science: Mathematics", 19),
    ("Mythology", 20),
    ("Sports", 21),
    ("Geography", 22),
    ("History", 23),
    ("Politics", 24),
    ("Art", 25),
    ("Celebrities", 26),
    ("Animals", 27),
    ("Vehicles", 28),
    ("Entertainment: Comics", 29),
    ("Science: Gadgets", 30),
    ("Entertainment: Japanese Anime & Manga", 31),
    ("Entertainment: Cartoon & Animations", 32)
]


# Function to generate choices dynamically
def category_choices():
    return [Choice(name=name, value=str(id_)) for name, id_ in CATEGORIES]


# Global scores dictionary
scores = {}


class Trivia(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.active_channels = set()
        self.scores = {}

    async def fetch_scores(self, user_id, guild_id):
        score = await self.bot.db.fetchone(
            f"SELECT correct, wrong FROM trivia_scores WHERE user_id = {user_id} AND guild_id = {guild_id}"
        )
        return {'correct': score[0], 'wrong': score[1]} if score else {'correct': 0, 'wrong': 0}

    async def fetch_all_scores(self, guild_id):
        res = await self.bot.db.fetchall(
            "SELECT user_id, correct, wrong FROM trivia_scores WHERE guild_id = %s",
            (int(guild_id),)
        )
        return {row[0]: {'correct': row[1], 'wrong': row[2]} for row in res}

    async def save_scores(self, user_id, guild_id, correct, wrong):
        await self.bot.db.commit(
            f"REPLACE INTO trivia_scores (user_id, guild_id, correct, wrong)"
            f" VALUES ({user_id}, {guild_id}, {correct}, {wrong})"
        )

    async def update_scores(self, user_id, guild_id, correct=False):
        score = await self.fetch_scores(int(user_id), int(guild_id))
        if correct:
            score['correct'] += 1
        else:
            score['wrong'] += 1
        await self.save_scores(user_id, guild_id, score['correct'], score['wrong'])

    @app_commands.command(
        name="trivia",
        description="Play a trivia game!"
    )
    @app_commands.choices(category=category_choices())
    async def trivia(self, ctx, category: str):
        channel_id = ctx.channel.id
        game_started = False

        # Check if a trivia game is already active in this channel
        if channel_id in self.active_channels:
            await ctx.response.send_message("A trivia is still waiting for an answer.")
            return

        self.active_channels.add(channel_id)

        formatted_question, correct_answer, choices = self.fetch_trivia_question(category)
        if not correct_answer or not choices:
            await ctx.send(formatted_question)  # this will send the error message
            return

        game_started = True

        # Send the question
        await ctx.response.send_message(formatted_question)
        start_time = ctx.created_at  # Timestamp when the command was invoked

        user_id = str(ctx.user.id)
        if user_id not in self.scores:
            self.scores[user_id] = {'correct': 0, 'wrong': 0}

        # Add the check function here:
        def check_answer(message):
            # Cleaning the user input
            cleaned_content = message.content.upper().replace(".", "")
            valid_content = ['A', 'B', 'C', 'D'] + [choice.upper() for choice in choices]

            # Return True if the message is from the correct channel and not from the bot
            # and the cleaned message content is one of the accepted answers
            return message.channel == ctx.channel and message.author != self.bot.user and cleaned_content in valid_content

        while True:  # Keep looping until a correct answer or timeout
            if channel_id not in self.active_channels:
                break
            try:
                # Use the check function in wait_for
                msg = await self.bot.wait_for('message', check=check_answer, timeout=60)

                # Map prefixes to answers
                prefix_to_answer = {
                    'A': choices[0],
                    'B': choices[1],
                    'C': choices[2],
                    'D': choices[3]
                }
                # Check if the user has given a direct answer or a prefixed one
                if msg.content.upper() in [choice.upper() for choice in
                                           choices]:  # Use uppercased choices for comparison
                    given_answer = msg.content.capitalize()  # Format the answer to have the first character capitalized
                else:
                    given_answer = prefix_to_answer.get(
                        msg.content.upper()).capitalize()  # Ensure this answer is also properly formatted

                elapsed_time = (msg.created_at - start_time).total_seconds()
                if elapsed_time >= 60:  # Check if 60 seconds have passed since the command was invoked
                    await ctx.response.send_message(f"Time's up! The correct answer was: {correct_answer}")
                    break

                # Check if the answer is correct
                if given_answer and given_answer.lower() == correct_answer.lower():
                    await self.update_scores(str(msg.author.id), str(ctx.guild.id), correct=True)
                    await ctx.followup.send(f"{correct_answer} is correct!")
                    break
                else:
                    await self.update_scores(str(msg.author.id), str(ctx.guild.id), correct=False)
                    await ctx.followup.send(f"Wrong! The correct answer was: {correct_answer}")
                    break

            except asyncio.TimeoutError:
                await ctx.followup.send(f"Time's up! The correct answer was: {correct_answer}")
            finally:
                if game_started:
                    self.active_channels.remove(channel_id)

    @app_commands.command(
        name="triviarank",
        description="Show your trivia rank!"
    )
    async def triviarank(self, ctx):
        # Load the latest scores
        guild_id = ctx.guild.id
        all_scores = await self.fetch_all_scores(guild_id)

        # Sort scores by correct answers
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]['correct'], reverse=True)

        # Find the rank and stats of the invoking user
        user_id = ctx.user.id
        user_score = all_scores.get(user_id, None)  # Use .get to fetch the user score or None if not exists

        if user_score is None:
            await ctx.followup.send("You have not played trivia yet!")
            return

        rank = [idx for idx, (uid, _) in enumerate(sorted_scores, 1) if uid == user_id][0]

        embed = discord.Embed(
            title="Your Trivia Rank",
            description=f"Rank: #{rank}",
            color=random.randint(0, 0xFFFFFF)  # Random color
        )
        embed.add_field(name=ctx.user.display_name,
                        value=f"Correct: {user_score['correct']}, Wrong: {user_score['wrong']}",
                        inline=False)

        await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name="trivialeaderboard",
        description="Show trivia leaderboard!"
    )
    async def leaderboard(self, ctx):
        # Load the latest scores
        guild_id = ctx.guild.id
        self.scores = await self.fetch_all_scores(guild_id)

        # Sort scores by correct answers
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1]['correct'], reverse=True)

        embed = discord.Embed(
            title="Trivia Leaderboard",
            color=random.randint(0, 0xFFFFFF)  # Random color
        )

        for idx, (user_id, score) in enumerate(sorted_scores, 1):
            user = await self.bot.fetch_user(int(user_id))  # Fetch user from their ID
            user_name = user.display_name  # Get user's display name

            embed.add_field(name=f"{idx}. {user_name}",
                            value=f"Correct: {score['correct']}, Wrong: {score['wrong']}",
                            inline=False)

        await ctx.response.send_message(embed=embed)

    def fetch_trivia_question(self, category_id):
        # Call OpenTDB API to get a trivia question for the given category
        response = requests.get(f"https://opentdb.com/api.php?amount=1&category={category_id}&type=multiple")

        if response.status_code != 200:
            return "Failed to fetch trivia question. Please try again.", None, None

        data = response.json()
        if not data.get('results'):
            return "No questions available for the selected category.", None, None

        # Format the fetched question for display
        question_obj = data['results'][0]
        question = html.unescape(question_obj['question'])
        correct_answer = html.unescape(question_obj['correct_answer'])
        choices = [html.unescape(choice) for choice in question_obj['incorrect_answers']] + [correct_answer]
        random.shuffle(choices)  # Shuffle choices so the correct answer isn't always last

        formatted_question = f"{question}\nChoices:\n" + '\n'.join(choices)

        # Formatting choices with prefixes A, B, C, D
        prefix_mapping = ['A', 'B', 'C', 'D']
        formatted_choices = [f"{prefix}. {choice}" for prefix, choice in zip(prefix_mapping, choices)]
        formatted_question = f"{question}\n" + '\n'.join(formatted_choices)

        # Return the formatted question, correct answer, and choices        
        return formatted_question, correct_answer, choices


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Trivia(bot))
