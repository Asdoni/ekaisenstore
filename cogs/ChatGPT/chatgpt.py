import asyncio
import os

import discord
import openai
import requests.exceptions
from discord import app_commands, Message
from discord.ext import commands

# Constants
from bot import EGirlzStoreBot
from currencyExchangeRate import get_usd_exchange_rate
from formatter import format_number

MAX_HISTORY = 1
TOKEN_COST_GPT35 = {'input': 0.001 / 1000, 'output': 0.002 / 1000}  # Costs in $ per token for GPT-3.5
TOKEN_COST_GPT4 = {'input': 0.01 / 1000, 'output': 0.03 / 1000}  # Costs in $ per token for GPT-4

MIN_COST_DISPLAY = 0.0001
MAX_EMBED_DESCRIPTION_LENGTH = 4096

# Environment variables
openai.api_key = os.getenv('OPENAI_KEY')

tones = {
    0: ["Normal", "Respond normally: "],
    1: ["Angry", "Respond angrily: "],
    2: ["Foolish", "Respond foolishly: "],
    3: ["Mad Scientist", "Respond like a mad scientist: "],
    4: ["Excited", "Respond excitedly: "],
    5: ["Sarcastic", "Respond sarcastically: "],
    6: ["Sympathetic", "Respond sympathetically: "],
    7: ["Humorous", "Respond humorously: "],
    8: ["Mysterious", "Respond mysteriously: "],
    9: ["Cat-like", "Respond like a cat: "],
    10: ["Main Villain", "Respond like a main villain: "],
    11: ["Habibi", "Respond like an Arab Habibi: "],
    12: ["Inspirational", "Respond inspirationally: "],
    13: ["Authoritative", "Respond with authority: "],
    14: ["Whimsical", "Respond whimsically: "],
    15: ["Philosophical", "Respond like a philosopher: "],
    16: ["Young Slang", "Respond with young people slang: "],
    17: ["Elderly Speak", "Respond like an elderly person: "],
    18: ["Spicy", "Respond with spicy novel-style intrigue: "],
    19: ["Pirate", "Respond in pirate speak:"],
    20: ["Gay", "Respond acting gay: "],
    21: ["Jamaican", "Resond like a 40 years old native Jamaican: "],
    22: ["UwU", "Respond in a kawaii anime style: "],
    23: ["Redneck", "Respond in a backwater southern redneck style: "],
    24: ["Drunk", "Respond like a drunk man: "],
}


def split_message(message: str, length: int) -> [str]:
    return [message[i:i + length] for i in range(0, len(message), length)]


def apply_tone(messages_payload, user_tone):
    if user_tone in tones and user_tone:
        messages_payload[-1]["content"] = tones[user_tone][1] + messages_payload[-1]["content"]
    return messages_payload


def calculate_cost(user_question, bot_answer, model):
    input_tokens = len(user_question.split())
    output_tokens = len(bot_answer.split())

    # Choose the correct token cost based on the model
    token_cost = TOKEN_COST_GPT35 if model.startswith("gpt-3.5") else TOKEN_COST_GPT4

    input_cost = input_tokens * token_cost['input']
    output_cost = output_tokens * token_cost['output']
    total_cost = input_cost + output_cost
    total_tokens_used = input_tokens + output_tokens
    return total_cost, total_tokens_used


async def send_bot_response(message, bot_answer, total_cost, total_tokens_used, user_tone, model_used):
    eur_cost = total_cost * get_usd_exchange_rate("EUR")
    cost_display = (
        f"€{format_number(eur_cost, 4)}"
        if eur_cost >= MIN_COST_DISPLAY
        else f"< €{format_number(MIN_COST_DISPLAY, 4)}"
    )
    # Get the tone name, default to "Unknown" if not found
    tone_display = tones.get(user_tone)[0] if user_tone in tones else "Unknown"
    model_display = "GPT-4" if model_used.startswith("gpt-4") else "GPT-3.5"

    for part in split_message(bot_answer, MAX_EMBED_DESCRIPTION_LENGTH):
        embed = discord.Embed(description=part, color=discord.Color.blue())
        embed.set_footer(
            text=(
                f"Model: {model_display} | Tokens used: {total_tokens_used} "
                f"| Cost: {cost_display} | Tone: {tone_display} "
            )
        )
        await message.reply(embed=embed)


class ChatGPT(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.conversation_histories = {}

    async def is_premium_guild(self, guild_id):
        result = await self.bot.db.fetchone("SELECT is_premium FROM premium_guilds WHERE guild_id = %s", (guild_id,))
        return result and result[0]

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or self.bot.user.id not in message.raw_mentions:
            return

        premium_guild = await self.is_premium_guild(message.guild.id)
        if not premium_guild:
            return
        self.bot.logger.info(f"Handling message from {message.author} in {message.guild}")
        user_question = message.content  # .replace(f"<@{self.bot.user.id}>", "").strip()
        user_history = [
            msg.content for msg in filter(
                lambda m: m.author.id == message.author.id and m != message,
                [msg async for msg in message.channel.history(limit=MAX_HISTORY)],
            )
        ]
        # Fetch user's preferred tone
        user_tone = await self.fetch_user_tone(message.author.id)

        asyncio.create_task(self.process_message(message, user_question, user_history, user_tone, premium_guild))

    async def fetch_user_tone(self, user_id):
        result = await self.bot.db.fetchone(f"SELECT tone FROM user_preferences WHERE user_id = {user_id}")
        return result[0] if result else 0  # 0 implies default tone

    async def process_message(self, message, user_question, user_history, user_tone, premium_guild):
        temp_message = await message.channel.send(
            embed=discord.Embed(description=f"Generating answer for {message.author.display_name}, please wait...",
                                color=discord.Color.orange()))
        messages_payload = [
            {
                "role": "system",
                "content": (
                    f"This is a Discord message."
                    f" Your a Discord-Bot with the id: {self.bot.user.id}."
                    f" List of the last Channel-Messages of the other user that you already answered successfully: "
                    f"{user_history}"
                )
            },
            {"role": "user", "content": user_question},
        ]

        # Apply tone to the user's message if necessary
        messages_payload = apply_tone(messages_payload, user_tone)

        response = await self.call_openai_api(messages_payload, premium_guild)
        await temp_message.delete()
        if response:
            model_used = "gpt-4-1106-preview" if premium_guild == 2 else "gpt-3.5-turbo-1106"
            bot_answer = response['choices'][0]['message']['content']
            total_cost, total_tokens_used = calculate_cost(user_question, bot_answer, model_used)
            await send_bot_response(message, bot_answer, total_cost, total_tokens_used, user_tone, model_used)
        else:
            await message.reply("There was an issue getting the response from the AI.")

    async def call_openai_api(self, messages_payload, premium_guild):
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }
        model = "gpt-4-1106-preview" if premium_guild == 2 else "gpt-3.5-turbo-1106"
        data = {
            "model": model,
            "messages": messages_payload,
            "max_tokens": 4096,
            "temperature": 0.5,
        }
        try:
            with self.bot.http_session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
            ) as resp:
                if resp.status_code == 200:
                    return resp.json()
                else:
                    self.bot.logger.error(f"OpenAI API error: {resp.status_code} - {resp.text}")
                    return None
        except requests.exceptions.ConnectTimeout:
            self.bot.logger.error("The request timed out")
        except requests.exceptions.HTTPError as e:
            self.bot.logger.error(f"An HTTP client error occurred: {e}")
        # You can catch any other specific exceptions you want here
        return None

    @app_commands.command(description="Set your preferred tone for ChatGPT responses.")
    @app_commands.choices(tone=[app_commands.Choice(name=val[0], value=key) for key, val in tones.items()])
    async def tone(self, interaction: discord.Interaction, tone: app_commands.Choice[int]):
        await self.bot.db.commit(
            (
                f"REPLACE INTO user_preferences (user_id, tone) "
                f"VALUES ({interaction.user.id}, {tone.value})"
            )
        )
        await interaction.response.send_message(f"Your preferred tone has been set to {tone.name}.", ephemeral=True)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(ChatGPT(bot))
