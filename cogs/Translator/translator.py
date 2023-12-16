import random

import discord
from discord import app_commands, Interaction, Member
from discord.app_commands import Choice
from discord.ext import commands
from googletrans import Translator, LANGUAGES

from bot import EGirlzStoreBot
from slashCommandCustomErrors import TranslationError

FLAG_EMOJI_TO_LANGUAGE = {
    "🇬🇧": "en",
    "🇺🇸": "en",
    "🇪🇸": "es",
    "🇲🇽": "es",
    "🇮🇹": "it",
    "🇩🇪": "de",
    "🇫🇷": "fr",
    "🇨🇳": "zh-CN",
    "🇯🇵": "ja",
    "🇷🇺": "ru",
    "🇧🇷": "pt",
    "🇵🇹": "pt",
    "🇳🇱": "nl",
    "🇸🇪": "sv",
    "🇦🇷": "es",
    "🇨🇴": "es",
    "🇰🇷": "ko",
    "🇸🇦": "ar",
    "🇮🇱": "he",
    "🇹🇷": "tr",
    "🇩🇰": "da",
    "🇧🇪": "nl",  # Belgian flag for Dutch
    "🇬🇷": "el",  # Greek
    "🇵🇱": "pl",  # Polish
    "🇨🇿": "cs"  # Czech
}

LANG_CODES_TO_NAMES = {code: name.capitalize() for code, name in LANGUAGES.items()}

# Generate the list of languages only for flags present in FLAG_EMOJI_TO_LANGUAGE dictionary.
TOP_25_LANGUAGES = list(FLAG_EMOJI_TO_LANGUAGE.keys())[:25]
limited_languages = [FLAG_EMOJI_TO_LANGUAGE[flag] for flag in TOP_25_LANGUAGES if flag in FLAG_EMOJI_TO_LANGUAGE]


# Error handling for translation


# Generate choices for app commanddef generate_choices():
def generate_choices():
    choices = []
    inverted_flag_emoji_to_language = {v: k for k, v in FLAG_EMOJI_TO_LANGUAGE.items()}
    added_languages = set()  # Track which languages we've already added

    for lang_code in limited_languages:
        lang_name = LANG_CODES_TO_NAMES.get(lang_code.lower(), lang_code)  # Use the language code as fallback
        if "-" in lang_name:  # This will handle cases like "zh-cn"
            lang_name, country_code = lang_name.split('-')
            lang_name = f"{LANGUAGES[lang_name].capitalize()} ({country_code.upper()})"
            # Get the flag emoji, or an empty string if not found
        flag_emoji = inverted_flag_emoji_to_language.get(lang_code, "")
        if lang_name not in added_languages:  # Check if the language is already added
            added_languages.add(lang_name)
            choices.append(Choice(name=lang_name, value=lang_code))
    return choices


def build_embed(author: Member, text: str, to: str):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=to)
        embed = discord.Embed(
            title=f"{author.display_name}",
            description=translation.text,
            color=discord.Colour(random.randint(0, 0xFFFFFF)),
        )
        translation_src = LANGUAGES[translation.src.lower()].capitalize()
        translation_dest = LANGUAGES[translation.dest.lower()].capitalize()
        translation_src_code = translation.src.upper()
        translation_dest_code = translation.dest.upper()

        embed.add_field(
            name="Translation Details",
            value=f"From {translation_src} ({translation_src_code}) to {translation_dest} ({translation_dest_code})",
            inline=False
        )
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(
            text=f"Translation requested by {author.display_name}.",
            icon_url=author.display_avatar.url  # Use avatar_url
        )
        return embed
    except Exception as e:
        raise TranslationError(f"Failed to translate message")


class TranslatorCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.translated_messages = set()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        emoji = payload.emoji.name
        # Check if the message has already been translated for this emoji
        if (payload.message_id, emoji) in self.translated_messages:
            return
        if emoji in FLAG_EMOJI_TO_LANGUAGE:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            # Avoid translating messages from bots or messages that have embeds
            if message.author.bot or message.embeds:
                return
            embed = build_embed(message.author, message.content, FLAG_EMOJI_TO_LANGUAGE[emoji])
            await message.reply(embed=embed)
            # After successful translation, add the message_id and emoji to the set
            self.translated_messages.add((payload.message_id, emoji))

    @app_commands.command(
        name="translate",
        description="Translate a given text into the specified language"
    )
    @app_commands.choices(to=generate_choices())
    async def translate(self, interaction: Interaction, prompt: str, to: str):
        embed = build_embed(interaction.user, prompt, to)
        await interaction.response.send_message(embed=embed)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(TranslatorCog(bot))
