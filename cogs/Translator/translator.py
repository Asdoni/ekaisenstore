import random
import discord
from discord import app_commands, Interaction, Member
from discord.app_commands import Choice
from discord.ext import commands
from googletrans import Translator, LANGUAGES
from bot import EGirlzStoreBot
from slashCommandCustomErrors import TranslationError

# Mapping of flag emojis to their respective language codes
FLAG_EMOJI_TO_LANGUAGE = {
    "🇬🇧": "en", "🇺🇸": "en", "🇪🇸": "es", "🇲🇽": "es", "🇮🇹": "it",
    "🇩🇪": "de", "🇫🇷": "fr", "🇨🇳": "zh-CN", "🇯🇵": "ja", "🇷🇺": "ru",
    "🇧🇷": "pt", "🇵🇹": "pt", "🇳🇱": "nl", "🇸🇪": "sv", "🇦🇷": "es",
    "🇨🇴": "es", "🇰🇷": "ko", "🇸🇦": "ar", "🇮🇱": "he", "🇹🇷": "tr",
    "🇩🇰": "da", "🇧🇪": "nl", "🇬🇷": "el", "🇵🇱": "pl", "🇨🇿": "cs"
}

# Mapping of Google Translate language codes to their names
LANG_CODES_TO_NAMES = {code: name.capitalize() for code, name in LANGUAGES.items()}

# Generate the list of language choices for flags present in FLAG_EMOJI_TO_LANGUAGE
TOP_25_LANGUAGES = list(FLAG_EMOJI_TO_LANGUAGE.keys())[:25]
limited_languages = [FLAG_EMOJI_TO_LANGUAGE[flag] for flag in TOP_25_LANGUAGES if flag in FLAG_EMOJI_TO_LANGUAGE]

def generate_choices():
    """
    Generates language choices for the translation command.
    """
    choices = []
    inverted_flag_emoji_to_language = {v: k for k, v in FLAG_EMOJI_TO_LANGUAGE.items()}
    added_languages = set()

    for lang_code in limited_languages:
        lang_name = LANG_CODES_TO_NAMES.get(lang_code.lower(), lang_code)
        if "-" in lang_name:
            lang_name, country_code = lang_name.split('-')
            lang_name = f"{LANGUAGES[lang_name].capitalize()} ({country_code.upper()})"
        flag_emoji = inverted_flag_emoji_to_language.get(lang_code, "")
        if lang_name not in added_languages:
            added_languages.add(lang_name)
            choices.append(Choice(name=f"{flag_emoji} {lang_name}", value=lang_code))
    return choices

def build_embed(author: Member, reacting_user: Member, text: str, to: str):
    """
    Builds a Discord embed with the translated text.
    """
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

        embed.add_field(
            name="Translation Details",
            value=f"From {translation_src} ({translation.src.upper()}) to {translation_dest} ({translation.dest.upper()})",
            inline=False
        )
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(
            text=f"Translation requested by {reacting_user.display_name}.",
            icon_url=reacting_user.display_avatar.url
        )
        return embed
    except Exception as e:
        raise TranslationError(f"Failed to translate message")

class TranslatorCog(commands.Cog):
    """
    Cog for handling translation features.
    """

    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.translated_messages = set()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Handles reaction events to translate messages.
        """
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
        """
        Slash command to translate text into a specified language.
        """
        embed = build_embed(interaction.user, interaction.user, prompt, to)
        await interaction.response.send_message(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(TranslatorCog(bot))
