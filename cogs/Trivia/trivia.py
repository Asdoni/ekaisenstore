import asyncio
import aiohttp
import html
import random

import discord
import requests
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

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

def category_choices():
    return [Choice(name=name, value=str(id_)) for name, id_ in CATEGORIES]

scores = {}

class Trivia(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.active_channels = set()
        self.scores = {}

    async def fetch_scores(self, user_id, guild_id):
        score = await self.bot.db.fetchone(
            "SELECT correct, wrong FROM trivia_scores WHERE user_id = $1 AND guild_id = $2",
            user_id, guild_id
        )
        return {'correct': score['correct'], 'wrong': score['wrong']} if score else {'correct': 0, 'wrong': 0}

    async def fetch_all_scores(self, guild_id):
        res = await self.bot.db.fetchall(
            "SELECT user_id, correct, wrong FROM trivia_scores WHERE guild_id = $1",
            guild_id
        )
        return {row['user_id']: {'correct': row['correct'], 'wrong': row['wrong']} for row in res}

    async def save_scores(self, user_id, guild_id, correct, wrong):
        await self.bot.db.execute(
            "INSERT INTO trivia_scores (user_id, guild_id, correct, wrong) VALUES ($1, $2, $3, $4) "
            "ON CONFLICT (user_id, guild_id) DO UPDATE SET correct = $3, wrong = $4",
            user_id, guild_id, correct, wrong
        )

    async def update_scores(self, user_id, guild_id, correct=False):
        score = await self.fetch_scores(user_id, guild_id)
        if correct:
            score['correct'] += 1
        else:
            score['wrong'] += 1
        await self.save_scores(user_id, guild_id, score['correct'], score['wrong'])

    async def fetch_trivia_question(self, category_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://opentdb.com/api.php?amount=1&category={category_id}&type=multiple") as response:
                if response.status != 200:
                    return "Failed to fetch trivia question. Please try again.", None, None

                data = await response.json()
                if not data.get('results'):
                    return "No questions available for the selected category.", None, None

                question_obj = data['results'][0]
                question = html.unescape(question_obj['question'])
                correct_answer = html.unescape(question_obj['correct_answer'])
                choices = [html.unescape(choice) for choice in question_obj['incorrect_answers']] + [correct_answer]
                random.shuffle(choices)

                formatted_choices = [f"{chr(65+i)}. {choice}" for i, choice in enumerate(choices)]
                formatted_question = f"{question}\n" + '\n'.join(formatted_choices)

                return formatted_question, correct_answer, choices

    @app_commands.command(
        name="trivia",
        description="Play a trivia game!"
    )
    @app_commands.choices(category=category_choices())
    async def trivia(self, interaction: discord.Interaction, category: str):
        channel_id = interaction.channel.id
        game_started = False

        if channel_id in self.active_channels:
            await interaction.response.send_message("A trivia is still waiting for an answer.")
            return

        self.active_channels.add(channel_id)

        formatted_question, correct_answer, choices = self.fetch_trivia_question(category)
        if not correct_answer or not choices:
            await interaction.send(formatted_question)
            return

        game_started = True

        await interaction.response.send_message(formatted_question)
        start_time = interaction.created_at 

        user_id = str(interaction.user.id)
        if user_id not in self.scores:
            self.scores[user_id] = {'correct': 0, 'wrong': 0}

        def check_answer(message):
            cleaned_content = message.content.upper().replace(".", "")
            valid_content = ['A', 'B', 'C', 'D'] + [choice.upper() for choice in choices]

            return message.channel == interaction.channel and message.author != self.bot.user and cleaned_content in valid_content

        while True:
            if channel_id not in self.active_channels:
                break
            try:
                msg = await self.bot.wait_for('message', check=check_answer, timeout=60)

                prefix_to_answer = {
                    'A': choices[0],
                    'B': choices[1],
                    'C': choices[2],
                    'D': choices[3]
                }
                if msg.content.upper() in [choice.upper() for choice in
                                           choices]:
                    given_answer = msg.content.capitalize() 
                else:
                    given_answer = prefix_to_answer.get(
                        msg.content.upper()).capitalize()

                elapsed_time = (msg.created_at - start_time).total_seconds()
                if elapsed_time >= 60:
                    await interaction.response.send_message(f"Time's up! The correct answer was: {correct_answer}")
                    break

                if given_answer and given_answer.lower() == correct_answer.lower():
                    await self.update_scores(str(msg.author.id), str(interaction.guild.id), correct=True)
                    await interaction.followup.send(f"{correct_answer} is correct!")
                    break
                else:
                    await self.update_scores(str(msg.author.id), str(interaction.guild.id), correct=False)
                    await interaction.followup.send(f"Wrong! The correct answer was: {correct_answer}")
                    break

            except asyncio.TimeoutError:
                await interaction.followup.send(f"Time's up! The correct answer was: {correct_answer}")
            finally:
                if game_started:
                    self.active_channels.remove(channel_id)

    @app_commands.command(
        name="triviarank",
        description="Show your trivia rank!"
    )
    async def triviarank(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        all_scores = await self.fetch_all_scores(guild_id)
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]['correct'], reverse=True)
        user_id = interaction.user.id
        user_score = all_scores.get(user_id, None)

        if user_score is None:
            await interaction.followup.send("You have not played trivia yet!")
            return

        rank = [idx for idx, (uid, _) in enumerate(sorted_scores, 1) if uid == user_id][0]

        embed = discord.Embed(
            title="Your Trivia Rank",
            description=f"Rank: #{rank}",
            color=random.randint(0, 0xFFFFFF)
        )
        embed.add_field(name=interaction.user.display_name,
                        value=f"Correct: {user_score['correct']}, Wrong: {user_score['wrong']}",
                        inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="trivialeaderboard",
        description="Show trivia leaderboard!"
    )
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        self.scores = await self.fetch_all_scores(guild_id)
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1]['correct'], reverse=True)

        embed = discord.Embed(
            title="Trivia Leaderboard",
            color=random.randint(0, 0xFFFFFF)
        )

        for idx, (user_id, score) in enumerate(sorted_scores, 1):
            user = await self.bot.fetch_user(int(user_id))
            user_name = user.display_name

            embed.add_field(name=f"{idx}. {user_name}",
                            value=f"Correct: {score['correct']}, Wrong: {score['wrong']}",
                            inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Trivia(bot))
