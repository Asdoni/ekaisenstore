import io
import discord
from discord.ext import commands
from discord import app_commands
import importlib.util

from bot import EGirlzStoreBot

def load_petpetgif():
    spec = importlib.util.spec_from_file_location("petpetgif", "/path/to/petpetgif.py")
    petpetgif = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(petpetgif)
    return petpetgif

class Pet(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.petpetgif = load_petpetgif()

    @app_commands.command(name="pet", description="Pet your or someone else's avatar")
    async def pet(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer(ephemeral=False)
        user = user or interaction.user
        thumbnail_url = user.display_avatar.url

        if user == interaction.user:
            embed = discord.Embed(
                title=f"Oh, {user.name}! 🤗",
                description="You're petting yourself... and loving it! It's important to love oneself!",
                color=discord.Color.blue()
            )
        elif user.bot and user.id != self.bot.user.id:
            embed = discord.Embed(
                title="Beep boop 🤖",
                description=f"{user.name} appreciates the gesture but wonders why a human is petting a machine.",
                color=discord.Color.gold()
            )
        elif user.id == self.bot.user.id:
            embed = discord.Embed(
                title="Awww 💖",
                description="Thanks for the pets! I feel loved and appreciated. 😊",
                color=discord.Color.red()
            )
        else:
            avatar_bytes = await user.display_avatar.replace(format="png", size=128).read()
            source = io.BytesIO(avatar_bytes)
            dest = io.BytesIO()

            self.petpetgif.petpet.make(source, dest)
            dest.seek(0)

            file = discord.File(dest, filename=f"{user.name}-pet.gif")
            embed = discord.Embed(title="Here's your petted avatar!", color=0x00ff00)
            await interaction.followup.send(file=file, embed=embed)
            return

        embed.set_thumbnail(url=thumbnail_url).set_footer(text="Enjoy your petting!")
        await interaction.followup.send(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Pet(bot))
