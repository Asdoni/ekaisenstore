import os
import openai
from discord import app_commands
from discord.ext import commands
from aiohttp import ClientTimeout, ClientError
import discord
import aiomysql
import asyncio
import logging
import aiohttp

# Constants
MAX_HISTORY = 1
TOKEN_COST_GPT35 = {'input': 0.001 / 1000, 'output': 0.002 / 1000}  # Costs in $ per token for GPT-3.5
TOKEN_COST_GPT4 = {'input': 0.01 / 1000, 'output': 0.03 / 1000}  # Costs in $ per token for GPT-4

MIN_COST_DISPLAY = 0.0001
MAX_EMBED_DESCRIPTION_LENGTH = 4096

# Set up logging
logging.basicConfig(level=logging.INFO)

# Environment variables
openai.api_key = os.getenv('OPENAI_KEY')
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
}

# Bot configuration
YOUR_USER_ID = 891679171279982602

async def is_premium_guild(pool, guild_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT is_premium FROM premium_guilds WHERE guild_id = %s", (guild_id,))
            result = await cur.fetchone()
            return result and result[0]

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_histories = {}
        self.db_pool = None
        bot.loop.create_task(self.setup())  # Schedule the setup task

    async def setup(self):
        try:
            self.db_pool = await aiomysql.create_pool(**DB_CONFIG, loop=self.bot.loop)
        except Exception as e:
            logging.error(f"Failed to create database pool: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content.startswith(f"<@{YOUR_USER_ID}>"):
            return

        premium_guild = await is_premium_guild(self.db_pool, message.guild.id)
        if not premium_guild:
            return

        logging.info(f"Handling message from {message.author} in {message.guild}")
        user_question = message.content.replace(f"<@{YOUR_USER_ID}>", "").strip()
        user_history = self.conversation_histories.get(message.author.id, [])[-(2 * MAX_HISTORY):]

        # Fetch user's preferred tone
        user_tone = await self.fetch_user_tone(message.author.id)
        
        asyncio.create_task(self.process_message(message, user_question, user_history, user_tone, premium_guild))

    async def fetch_user_tone(self, user_id):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT tone FROM user_preferences WHERE user_id = %s", (user_id,))
                result = await cur.fetchone()
                return result[0] if result else 0  # 0 implies default tone

    async def process_message(self, message, user_question, user_history, user_tone, premium_guild):
        temp_message = await message.channel.send(embed=discord.Embed(description=f"Generating answer for {message.author.display_name}, please wait...", color=discord.Color.orange()))
        messages_payload = [{"role": "system", "content": "This is a Discord message"}, *user_history, {"role": "user", "content": user_question}]

        # Apply tone to the user's message if necessary
        messages_payload = self.apply_tone(messages_payload, user_tone)

        response = await self.call_openai_api(messages_payload, premium_guild)
        await temp_message.delete()
        if response:
            model_used = "gpt-4-1106-preview" if premium_guild == 2 else "gpt-3.5-turbo-1106"
            bot_answer = response['choices'][0]['message']['content']
            total_cost, total_tokens_used = self.calculate_cost(user_question, bot_answer, model_used)
            await self.send_bot_response(message, bot_answer, total_cost, total_tokens_used, user_tone, model_used)
        else:
            await message.reply("There was an issue getting the response from the AI.")

    def apply_tone(self, messages_payload, user_tone):
        tone_prefixes = {
            1: "Respond angrily: ",
            2: "Respond foolishly: ",
            3: "Respond like a mad scientist: ",
            4: "Respond excitedly: ",
            5: "Respond sarcastically: ",
            6: "Respond sympathetically: ",
            7: "Respond humorously: ",
            8: "Respond mysteriously: ",
            9: "Respond like a cat: ",
            10: "Respond like a main villain: ",
            11: "Respond like an Arab Habibi: ",
            12: "Respond inspirationally: ",
            13: "Respond with authority: ",
            14: "Respond whimsically: ",
            15: "Respond like a philosopher: ",
            16: "Respond with young people slang: ",
            17: "Respond like an elderly person: ",
            18: "Respond with spicy novel-style intrigue: ",
            19: "Respond in pirate speak:",
            20: "Respond acting gay: ",
            21: "Resond like a 40 years old native Jamaican: ",
            22: "Respond in a kawaii anime style: ",
            23: "Respond in a backwater southern redneck style: ",
            24: "Respond like a drunk man: ",
            # ... more tones can be added here
        }
        if user_tone in tone_prefixes:
            messages_payload[-1]["content"] = tone_prefixes[user_tone] + messages_payload[-1]["content"]
        return messages_payload

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
            "temperature": 0.5
        }

        # Set the timeout to 30 seconds
        timeout = ClientTimeout(total=300)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logging.error(f"OpenAI API error: {resp.status} - {await resp.text()}")
                        return None
        except asyncio.TimeoutError:
            logging.error("The request timed out")
        except ClientError as e:
            logging.error(f"An HTTP client error occurred: {e}")
        # You can catch any other specific exceptions you want here
        return None

    def calculate_cost(self, user_question, bot_answer, model):
        input_tokens = len(user_question.split())
        output_tokens = len(bot_answer.split())

        # Choose the correct token cost based on the model
        token_cost = TOKEN_COST_GPT35 if model.startswith("gpt-3.5") else TOKEN_COST_GPT4

        input_cost = input_tokens * token_cost['input']
        output_cost = output_tokens * token_cost['output']
        total_cost = input_cost + output_cost
        total_tokens_used = input_tokens + output_tokens
        return (total_cost, total_tokens_used)

    async def send_bot_response(self, message, bot_answer, total_cost, total_tokens_used, user_tone, model_used):
        tone_names = {
            0: "Normal",
            1: "Angry",
            2: "Foolish",
            3: "Mad Scientist",
            4: "Excited",
            5: "Sarcastic",
            6: "Sympathetic",
            7: "Humorous",
            8: "Mysterious",
            9: "Cat-like",
            10: "Main Villain",
            11: "Habibi",
            12: "Inspirational",
            13: "Authoritative",
            14: "Whimsical",
            15: "Philosophical",
            16: "Young Slang",
            17: "Elderly Speak",
            18: "Spicy",   
            19: "Pirate",
            20: "Gay",         
            21: "Jamaican",
            22: "UwU",
            23: "Redneck",
            24: "Drunk",
            # ... add more tones if necessary
        }
        cost_display = f"${total_cost:.4f}" if total_cost >= MIN_COST_DISPLAY else "< $0.0001"
        tone_display = tone_names.get(user_tone, "Unknown")  # Get the tone name, default to "Unknown" if not found
        model_display = "GPT-4" if model_used.startswith("gpt-4") else "GPT-3.5"

        for part in self.split_message(bot_answer, MAX_EMBED_DESCRIPTION_LENGTH):
            embed = discord.Embed(description=part, color=discord.Color.blue())
            embed.set_footer(text=f"Model: {model_display} | Tokens used: {total_tokens_used} | Cost: {cost_display} | Tone: {tone_display}")
            await message.reply(embed=embed)

    def split_message(self, message, length):
        return [message[i:i+length] for i in range(0, len(message), length)]

    async def cog_unload(self):
        self.db_pool.close()
        await self.db_pool.wait_closed()

    @app_commands.command(description="Set your preferred tone for ChatGPT responses.")
    @app_commands.choices(tone=[
        app_commands.Choice(name="Normal", value=0),
        app_commands.Choice(name="Angry", value=1),
        app_commands.Choice(name="Foolish", value=2),
        app_commands.Choice(name="Mad Scientist", value=3),
        app_commands.Choice(name="Excited", value=4),
        app_commands.Choice(name="Sarcastic", value=5),
        app_commands.Choice(name="Sympathetic", value=6),
        app_commands.Choice(name="Humorous", value=7),
        app_commands.Choice(name="Mysterious", value=8),
        app_commands.Choice(name="Cat-like", value=9),
        app_commands.Choice(name="Main Villain", value=10),
        app_commands.Choice(name="Habibi", value=11),
        app_commands.Choice(name="Inspirational", value=12),
        app_commands.Choice(name="Authoritative", value=13),
        app_commands.Choice(name="Whimsical", value=14),
        app_commands.Choice(name="Philosophical", value=15),
        app_commands.Choice(name="Young Slang", value=16),
        app_commands.Choice(name="Elderly Speak", value=17),
        app_commands.Choice(name="Spicy", value=18),
        app_commands.Choice(name="Pirate", value=19),
        app_commands.Choice(name="Gay", value=20),
        app_commands.Choice(name="Jamaican", value=21),
        app_commands.Choice(name="UwU", value=22),
        app_commands.Choice(name="Redneck", value=23),
        app_commands.Choice(name="Drunk", value=24),
        # ... add more choices if necessary
    ])
    async def tone(self, interaction: discord.Interaction, tone: app_commands.Choice[int]):
        user_id = interaction.user.id
        tone_value = tone.value

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO user_preferences (user_id, tone) VALUES (%s, %s) AS new_values
                    ON DUPLICATE KEY UPDATE tone = new_values.tone
                """, (user_id, tone_value))
                await conn.commit()

        await interaction.response.send_message(f"Your preferred tone has been set to {tone.name}.", ephemeral=True)

def setup(bot):
    chat_cog = ChatGPT(bot)
    bot.add_cog(chat_cog)
    bot.tree.add_command(chat_cog.tone)