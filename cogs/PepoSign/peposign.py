from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import discord
import os
import tempfile
import re
import string

from bot import EGirlzStoreBot

class PepoSign(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(name="peposign", description="Create a custom Pepo Sign")
    @app_commands.describe(text="The text to display on the sign")
    @app_commands.choices(pepe=[
        app_commands.Choice(name="PepoFlower", value="peposign1"),
        app_commands.Choice(name="PepoDank", value="peposign2"),
        app_commands.Choice(name="PepoHappy", value="peposign3")
    ])
    async def peposign(self, interaction: discord.Interaction, text: str, pepe: str = "peposign1"):
        # Check for custom emojis in the text
        if self.contains_custom_emoji(text):
            embed = discord.Embed(
                title="Oops! 🚫",
                description="Custom emojis are not allowed in the text. Please remove them and try again.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer()
        text = await self.resolve_mentions(interaction, text)
        text = await self.resolve_channel_mentions(interaction, text)
        text = await self.resolve_role_mentions(interaction, text)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_directory = os.path.join(current_dir, 'Assets')
        base_image_path = os.path.join(assets_directory, f"{pepe}.png")
        font_path = os.path.join(assets_directory, "NotoSans-Regular.ttf")

        image = Image.open(base_image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)
        text_box = (5, 10, image.width - 5, 46)

        font, wrapped_text, is_text_too_long = self.adjust_font_size(font_path, text, text_box[2] - text_box[0], text_box[3] - text_box[1])
        if is_text_too_long:
            embed = discord.Embed(
                title="Whoops! 🙈",
                description="Your text tried to do a marathon but ran out of breath!\nTry a shorter message. 🏃💨",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Let's keep it short and sweet! 🍰")
            embed.set_thumbnail(url="https://emojicdn.elk.sh/📜")
            embed.set_author(name="PepoSign", icon_url="https://emojicdn.elk.sh/✍️")
            return await interaction.followup.send(embed=embed)

        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text) + (len(wrapped_text) - 1) * 2

        y_offset = text_box[1] + ((text_box[3] - text_box[1] - total_text_height) / 2)

        for index, line in enumerate(wrapped_text):
            bbox = draw.textbbox((0, 0), line, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            x_offset = text_box[0] + ((text_box[2] - text_box[0] - width) / 2)
            draw.text((x_offset, y_offset), line, font=font, fill="black")
            y_offset += height + 2  # Slightly increased line spacing

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image.save(tmp.name)
            await interaction.followup.send(file=discord.File(tmp.name))

    def adjust_font_size(self, font_path, text, max_width, max_height):
        font_size = 46
        font = ImageFont.truetype(font_path, font_size)
        lines = self.wrap_text(text, font, max_width)
        total_height = self.calculate_total_height(lines, font)

        while total_height > max_height and font_size > 10:
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)
            lines = self.wrap_text(text, font, max_width)
            total_height = self.calculate_total_height(lines, font)

        return font, lines, total_height > max_height  # Adjusted condition to check against max_height

    def wrap_text(self, text, font, max_width):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F700-\U0001F77F"  # alchemical symbols
            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE)

        parts = emoji_pattern.split(text)
        words = []

        for part in parts:
            words += part.split()

        lines = []
        current_line = ""
        for word in words:
            bbox = font.getbbox(word)
            word_width = bbox[2] - bbox[0]
            if word_width > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                while word_width > max_width:
                    i = 1
                    while font.getbbox(word[:i])[2] - font.getbbox(word[:i])[0] < max_width and i < len(word):
                        i += 1
                    lines.append(word[:i-1])
                    word = word[i-1:]
                    word_width = font.getbbox(word)[2] - font.getbbox(word)[0]
                current_line = word
            else:
                test_line = f"{current_line} {word}".strip()
                test_line_width = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]
                if test_line_width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def calculate_total_height(self, lines, font):
        return sum(font.getbbox(line)[3] + 2 for line in lines) 
    
    def contains_custom_emoji(self, text):
        # Regex to find custom emojis
        pattern = re.compile(r"<a?:\w+:\d+>")
        return bool(pattern.search(text))
    
    async def resolve_mentions(self, interaction: discord.Interaction, text):
        words = text.split()
        resolved_text = []
        for word in words:
            if word.startswith('<@') and word.endswith('>'):
                id = word.strip('<@!>')
                try:
                    user = await interaction.guild.fetch_member(id)
                    resolved_text.append(user.display_name)
                except discord.NotFound:
                    resolved_text.append('@unknown-user')
                except Exception as e:
                    print(f"Error fetching user {id}: {str(e)}")
                    resolved_text.append(word)
            else:
                resolved_text.append(word)
        return ' '.join(resolved_text)

    def sanitize_text(self, text):
        allowed_chars = string.ascii_letters + string.digits + " _-"
        return ''.join(c for c in text if c in allowed_chars)

    async def resolve_channel_mentions(self, interaction: discord.Interaction, text):
        words = text.split()
        resolved_text = []
        for word in words:
            if word.startswith('<#') and word.endswith('>'):
                id = word.strip('<#>')
                try:
                    channel = await interaction.guild.fetch_channel(id)
                    channel_name = self.sanitize_text(channel.name)
                    resolved_text.append("#" + channel_name.strip())
                except discord.NotFound:
                    resolved_text.append('#unknown-channel')
                except Exception as e:
                    print(f"Error fetching channel {id}: {str(e)}")
                    resolved_text.append(word)
            else:
                resolved_text.append(word)
        return ' '.join(resolved_text)
    
    async def resolve_role_mentions(self, interaction: discord.Interaction, text):
        words = text.split()
        resolved_text = []
        for word in words:
            if word.startswith('<@&') and word.endswith('>'):
                id = word.strip('<@&>')
                try:
                    role = [r for r in await interaction.guild.fetch_roles() if r.id == int(id)]
                    if role:
                        resolved_text.append("@" + role[0].name)
                    else:
                        resolved_text.append('@unknown-role')
                except Exception as e:
                    print(f"Error fetching role {id}: {str(e)}")
                    resolved_text.append(word)
            else:
                resolved_text.append(word)
        return ' '.join(resolved_text)
    
async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(PepoSign(bot))