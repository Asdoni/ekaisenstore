import os
import aiohttp
import discord
import openai
import tiktoken
from discord import app_commands, Embed
from discord.ext import commands
from discord.errors import NotFound

from bot import EGirlzStoreBot
from currencyExchangeRate import get_usd_exchange_rate
from formatter import format_number

TOKEN_COST_GPT35 = {'input': 0.00000050, 'output': 0.00000150}
TOKEN_COST_GPT4 = {'input': 0.00001000, 'output': 0.00003000}
MIN_COST_DISPLAY = 0.0001
MAX_EMBED_DESCRIPTION_LENGTH = 4096
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
MODEL_GPT4 = 'gpt-4-0125-preview'
MODEL_GPT35 = 'gpt-3.5-turbo-0125'
TONES = {
    0: ["Normal", "Respond normally: "],
    1: ["Angry", "Respond angrily: "],
    2: ["Foolish", "Respond foolishly: "],
    3: ["Unpolite", "Respond unpolitely and angrily: "],
    4: ["Excited", "Respond excitedly: "],
    5: ["Sarcastic", "Respond sarcastically: "],
    6: ["Wrong", "Respond with a wrong answer:"],
    7: ["Humorous", "Respond humorously: "],
    8: ["Chef", "Respond like a chef: "],
    9: ["Cat-like", "Respond like a cat: "],
    10: ["Main Villain", "Respond like a main villain: "],
    11: ["Habibi", "Respond like an Arab Habibi: "],
    12: ["Inspirational", "Respond inspirationally: "],
    13: ["Friendly Banter", "Engage with a touch of friendly jest, a mix of light-hearted roasts and affectionate teasing: "],
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

openai.api_key = os.getenv('OPENAI_KEY')

def split_message(message: str, length: int) -> [str]:
    return [message[i:i + length] for i in range(0, len(message), length)]

def apply_tone(messages_payload, user_tone):
    if user_tone in TONES:
        tone_prefix = TONES[user_tone][1]
        messages_payload[-1]["content"] = tone_prefix + messages_payload[-1]["content"]
    return messages_payload

def calculate_cost(user_message, bot_answer, model):

    if model.startswith("gpt-3.5"):
        model_str = "gpt-3.5-turbo"
    else:
        model_str = "gpt-4"

    encoder = tiktoken.encoding_for_model(model_str)
    input_tokens = len(encoder.encode(user_message))
    output_tokens = len(encoder.encode(bot_answer))
    token_cost = TOKEN_COST_GPT35 if model.startswith("gpt-3.5") else TOKEN_COST_GPT4
    input_cost = input_tokens * token_cost['input']
    output_cost = output_tokens * token_cost['output']
    total_cost = input_cost + output_cost
    total_tokens_used = input_tokens + output_tokens
    return total_cost, total_tokens_used, input_cost, output_cost

class ChatGPT(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.premium_guilds_cache = set()
        self.user_tones_cache = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.content:
            return

        if message.content.startswith(f'<@!{self.bot.user.id}>') or message.content.startswith(f'<@{self.bot.user.id}>'):
            premium_status = await self.is_premium_guild(message.guild.id)
            if premium_status == 0:
                custom_message = "Ahoy! Looks like you're navigating the vast seas without a premium flag.\nUpgrade to premium for a treasure trove of exclusive features."
                embed = Embed(title="Premium Feature", description=custom_message, color=discord.Color.gold())
                image_path = 'cogs/ChatGPT/images/business.png'
                file = discord.File(image_path, filename="business.png")
                embed.set_thumbnail(url="attachment://business.png")
                embed.set_footer(text="Unlock the full potential of your guild with premium!")
                await message.reply(file=file, embed=embed)
                return
            elif premium_status == 1:
                model_used = MODEL_GPT35
            elif premium_status == 2:
                model_used = MODEL_GPT4

            user_tone = await self.fetch_user_tone(message.author.id, message.guild.id)

            content_without_mention = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            await self.process_message(message, content_without_mention, user_tone, False, model_used)

    async def is_premium_guild(self, guild_id):
        result = await self.bot.db.fetchone("SELECT is_premium FROM premium_guilds WHERE guild_id = $1", guild_id)
        return result[0] if result else 0
    
    async def fetch_user_tone(self, user_id, guild_id):
        result = await self.bot.db.fetchone("SELECT tone FROM user_preferences WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
        self.bot.logger.info(f"Fetched tone {result[0] if result else 'None'} for user {user_id}")
        return result[0] if result else 0

    async def process_message(self, message, user_message, user_tone, is_reply, model_used):
        temp_message = await message.channel.send(embed=Embed(description="Generating answer, please wait...", color=discord.Color.orange()))
        
        messages_payload = [{"role": "user", "content": user_message}]
        messages_payload = apply_tone(messages_payload, user_tone)
        
        self.bot.logger.info(f"Final payload with tone: {messages_payload}")
        response = await self.call_openai_api(messages_payload, is_reply, model_used)

        try:
            await temp_message.delete()
        except NotFound:
            pass

        if response == "quota_exceeded":
            custom_message = "You spent all Andoni money.\nPlease donate to Andoni to keep this service running."
            embed = Embed(title="Exceeded Quota", description=custom_message, color=discord.Color.red())
            image_path = 'cogs/ChatGPT/images/poor.png'
            file = discord.File(image_path, filename="poor.png")
            embed.set_thumbnail(url="attachment://poor.png")
            embed.set_footer(text="It was all Karpax fault! Blame him!")
            await message.reply(file=file, embed=embed)
        elif isinstance(response, dict):
            try:
                bot_answer = response['choices'][0]['message']['content']
                total_cost, total_tokens_used, input_cost, output_cost = calculate_cost(user_message, bot_answer, model_used)
                await self.send_bot_response(message, bot_answer, total_cost, total_tokens_used, user_tone, model_used)
            except KeyError:
                await message.reply("Unexpected response structure from OpenAI API.")
        else:
            await message.reply("There was an issue getting the response from the AI.")

            messages_payload = [{"role": "user", "content": user_message}]
            messages_payload = apply_tone(messages_payload, user_tone)
            response = await self.call_openai_api(messages_payload, is_reply)
            try:
                await temp_message.delete()
            except NotFound:
                pass

            if response:
                bot_answer = response['choices'][0]['message']['content']
                model_used = MODEL_GPT4 
                total_cost, total_tokens_used, input_cost, output_cost = calculate_cost(user_message, bot_answer, model_used)
                await self.send_bot_response(message, bot_answer, total_cost, total_tokens_used, user_tone, model_used)
            else:
                await message.reply(embed=Embed(description="There was an issue getting the response from the AI.", color=discord.Color.red()))

    async def send_bot_response(self, message, bot_answer, total_cost, total_tokens_used, user_tone, model_used):
        eur_cost = total_cost * get_usd_exchange_rate("EUR")
        cost_display = f"€{format_number(eur_cost, 4)}" if eur_cost >= MIN_COST_DISPLAY else f"< €{format_number(MIN_COST_DISPLAY, 4)}"
        tone_display = TONES.get(user_tone)[0] if user_tone in TONES else "Unknown"

        if model_used == MODEL_GPT4:
            model_display = "GPT-4"
        elif model_used == MODEL_GPT35:
            model_display = "GPT-3.5"
        else:
            model_display = "Unknown Model"

        bot_answer_parts = split_message(bot_answer, MAX_EMBED_DESCRIPTION_LENGTH)
        for part in bot_answer_parts:
            embed = discord.Embed(description=part, color=discord.Color.blue())
            embed.set_footer(text=f"Model: {model_display} | Tokens used: {total_tokens_used} | Cost: {cost_display} | Tone: {tone_display}")
            await message.reply(embed=embed)

    async def call_openai_api(self, messages_payload, is_reply, model_used):
        headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json"}
        model = MODEL_GPT4 if is_reply else MODEL_GPT35
        data = {"model": model_used, "messages": messages_payload, "max_tokens": 4096, "temperature": 0.5}

        self.bot.logger.info(f"Sending payload: {messages_payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(OPENAI_API_URL, headers=headers, json=data) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 429:
                    self.bot.logger.error("OpenAI API error: Quota exceeded")
                    return "quota_exceeded"
                else:
                    self.bot.logger.error(f"OpenAI API error: {resp.status} - {await resp.text()}")
        return None

    @app_commands.command(description="Set your preferred tone for ChatGPT responses.")
    @app_commands.choices(tone=[app_commands.Choice(name=val[0], value=key) for key, val in TONES.items()])
    async def tone(self, interaction: discord.Interaction, tone: app_commands.Choice[int]):
        query = """
        INSERT INTO user_preferences (user_id, guild_id, tone) VALUES ($1, $2, $3)
        ON CONFLICT (user_id, guild_id) DO UPDATE SET tone = EXCLUDED.tone
        """
        self.bot.logger.info(f"Setting tone: {tone.value} for user: {interaction.user.id} in guild: {interaction.guild_id}")
        await self.bot.db.execute(query, interaction.user.id, interaction.guild_id, tone.value)
        self.bot.logger.info("Tone set successfully")

        await interaction.response.send_message(f"Your preferred tone has been set to {tone.name}.", ephemeral=True)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(ChatGPT(bot))