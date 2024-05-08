import discord
import random
from datetime import datetime
from discord import app_commands, Embed
from discord.ext import commands

from bot import EGirlzStoreBot

def get_booby_line(size: int, amount=2) -> str:
    spaces = ' \u200B' * size
    return f'({spaces}.{spaces})' * amount

class BB(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    def generate_regular_description(self, user_display_name):
        bb_not_found = False
        triple_boob = False
        random_chance = random.randint(1, 100)
        bb_not_found = random_chance <= 3.5
        triple_boob = random_chance >= 95
        random_size = random.randint(0, 9) if not bb_not_found and not triple_boob else None

        if bb_not_found:
            description = "I'm sorry, you are flat! <:smolpp:1062443373165822022>"
            title = f"{user_display_name}'s bb - Flat as a board!"
        elif triple_boob:
            description = get_booby_line(4, 3)
            title = f"{user_display_name} - Triple the fun!"
        else:
            cup_sizes = "ABCDEFGHI"
            cup_size = 'AA' if random_size == 0 else cup_sizes[random_size - 1]
            description = get_booby_line(random_size * 2)
            title = f"{user_display_name}'s Cup size {cup_size}!"
        return title, description

    @app_commands.command(name="bb", description="Measure your boobies")
    async def boobies(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        today = datetime.now()
        random_color = random.randint(0, 0xFFFFFF)

        if today.month == 4 and today.day == 1:
            scenario = random.randint(1, 4)
            if scenario == 1:
                title, description = self.generate_regular_description(interaction.user.display_name)
            elif scenario == 2:
                # Descriptions
                descriptions = [
                    "radiate with the energy of a thousand suns, truly awe-inspiring!",
                    "have their own gravitational pull, defying the laws of physics!",
                    "are so majestic, they've been declared a national treasure.",
                    "are so enchanting, they've inspired countless poets.",
                    "are imbued with magical properties, granting wishes to the pure of heart.",
                    "emit wifi signals, providing internet wherever you go.",
                    "glow in the dark, leading the way through the darkest nights.",
                    "are so harmonious, birds sing when you're near.",
                    "can predict the weather, making you the ultimate weather forecast.",
                    "are so legendary, myths speak of their greatness.",
                ]
                description = f"{interaction.user.mention}, your boobies {random.choice(descriptions)}"
                title = f"{interaction.user.display_name}'s boobies have superpowers!"
            elif scenario == 3:
                # Compliments
                compliments = [
                    "are inspiring sonnets and songs across the globe.",
                    "have been voted the Eighth Wonder of the World.",
                    "are so legendary, they're rumored to grant eternal youth.",
                    "sparkle brighter than the stars in the night sky.",
                    "possess a magnetic charm that captivates everyone's heart.",
                    "are the subject of fairy tales and epic sagas.",
                    "exude an aura of elegance that royalty would envy.",
                    "are a treasure more precious than the rarest jewels.",
                    "hold the secret to happiness and eternal joy.",
                    "are a masterpiece celebrated by artists and poets alike.",
                ]
                description = f"{interaction.user.mention}, your boobies {random.choice(compliments)}"
                title = f"{interaction.user.display_name}'s boobies are out of this world!"
            elif scenario == 4:
                # Roasts
                roasts =  [
                    "are like Bigfoot; highly talked about but never actually seen.",
                    "are so undercover, not even the FBI can find them.",
                    "could be used as a stealth model for avoiding radar detection.",
                    "are playing a game of hide and seek. Spoiler: they're winning.",
                    "are so exclusive, they haven't made their debut yet.",
                    "are like a minimalist art piece: less is more, right?",
                    "have been classified as an endangered species: very rare and elusive.",
                    "are so flat, they're often mistaken for the Great Plains.",
                    "are like Wi-Fi signals: the closer you are, the stronger they get. Just kidding, there's no signal.",
                    "are so eco-friendly, they leave absolutely no footprint.",
                ]
                description = f"{interaction.user.mention}, your boobies {random.choice(roasts)}"
                title = f"{interaction.user.display_name}'s boobies? What boobies?"
        else:
            # Regular functionality
            title, description = self.generate_regular_description(interaction.user.display_name)

        embed = Embed(title=title, description=description, color=random_color)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(BB(bot))