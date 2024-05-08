import os
import random
import discord
from discord import app_commands, Interaction, Member
from discord.app_commands import Choice
from discord.ext import commands

import deepl
from langdetect import detect

from bot import EGirlzStoreBot
from slashCommandCustomErrors import TranslationError

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

translator = deepl.Translator(DEEPL_API_KEY)

FLAG_EMOJI_TO_LANGUAGE = {
    "🇬🇧": "EN-GB",
    "🇺🇸": "EN-US",
    "🇩🇪": "DE",
    "🇫🇷": "FR",
    "🇪🇸": "ES",
    "🇮🇹": "IT",
    "🇳🇱": "NL",
    "🇵🇱": "PL",
    "🇷🇺": "RU",
    "🇯🇵": "JA",
    "🇨🇳": "ZH",
    "🇵🇹": "PT-PT",
    "🇧🇷": "PT-BR",
    "🇩🇰": "DA",
    "🇫🇮": "FI",
    "🇬🇷": "EL",
    "🇭🇺": "HU",
    "🇮🇩": "ID",
    "🇰🇷": "KO",
    "🇳🇴": "NB",
    "🇷🇴": "RO",
    "🇸🇰": "SK",
    "🇸🇮": "SL",
    "🇸🇪": "SV",
    "🇹🇷": "TR"
}

LANG_CODES_TO_NAMES = {
    "EN-GB": "English (UK)",
    "EN-US": "English (US)",
    "DE": "German",
    "FR": "French",
    "ES": "Spanish",
    "IT": "Italian",
    "NL": "Dutch",
    "PL": "Polish",
    "RU": "Russian",
    "JA": "Japanese",
    "ZH": "Chinese",
    "PT-PT": "Portuguese (Portugal)",
    "PT-BR": "Portuguese (Brazil)",
    "DA": "Danish",
    "FI": "Finnish",
    "EL": "Greek",
    "HU": "Hungarian",
    "ID": "Indonesian",
    "KO": "Korean",
    "NB": "Norwegian (Bokmål)",
    "RO": "Romanian",
    "SK": "Slovak",
    "SL": "Slovenian",
    "SV": "Swedish",
    "TR": "Turkish"
}


def generate_choices():
    choices = []
    for flag, lang_code in FLAG_EMOJI_TO_LANGUAGE.items():
        lang_name = LANG_CODES_TO_NAMES.get(lang_code, "")
        choices.append(Choice(name=f"{flag} {lang_name}", value=lang_code))
    return choices

from langdetect import detect

def build_embed(author: Member, reacting_user: Member, text: str, to: str):
    try:
        source_lang_code = detect(text)
        source_lang_name = LANG_CODES_TO_NAMES.get(source_lang_code.upper(), "Unknown language")
        
        translation = translator.translate_text(text, target_lang=to)
        embed = discord.Embed(
            title=f"{author.display_name}",
            description=translation.text,
            color=discord.Colour(random.randint(0, 0xFFFFFF)),
        )
        target_lang_name = LANG_CODES_TO_NAMES.get(to.upper(), to)
        embed.add_field(
            name="Translation Details",
            value=f"From {source_lang_name} ({source_lang_code.upper()}) to {target_lang_name} ({to})",
            inline=False
        )
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(
            text=f"Translation requested by {reacting_user.display_name}.",
            icon_url=reacting_user.display_avatar.url
        )
        return embed
    except Exception as e:
        raise TranslationError(f"Failed to translate message: {str(e)}")


class TranslatorCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.translated_messages = set()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        emoji = payload.emoji.name
        if (payload.message_id, emoji) in self.translated_messages:
            return
        if emoji in FLAG_EMOJI_TO_LANGUAGE:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.author.bot or message.embeds:
                return
            reacting_user = await self.bot.fetch_user(payload.user_id)
            embed = build_embed(message.author, reacting_user, message.content, FLAG_EMOJI_TO_LANGUAGE[emoji])
            await message.reply(embed=embed)
            self.translated_messages.add((payload.message_id, emoji))

    @app_commands.command(
        name="translate",
        description="Translate a given text into the specified language"
    )
    @app_commands.choices(to=generate_choices())
    async def translate(self, interaction: Interaction, prompt: str, to: str):
        embed = build_embed(interaction.user, interaction.user, prompt, to)
        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(TranslatorCog(bot))
