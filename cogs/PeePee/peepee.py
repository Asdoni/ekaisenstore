import discord
from random import randint, choice
from datetime import datetime

from discord import app_commands, Embed
from discord.ext import commands

from bot import EGirlzStoreBot


class PP(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="pp",
        description="Measure your PP"
    )
    async def peepee(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        today = datetime.now()

        pp_length = None
        
        title = f"{interaction.user.display_name}'s PP is {pp_length} CM"

        if today.month == 4 and today.day == 1:
            scenario = randint(1, 4)
            if scenario == 1:
                pp_length = randint(1, 30) if randint(0, 99) else 100
                description = f"8{'=' * pp_length}>"
            elif scenario == 2:
                # Compliments
                compliments = [
                    "astonishingly brilliant, as if your brain runs on a supercomputer",
                    "unbelievably lucky, as though you've found a field of four-leaf clovers",
                    "incredibly charming, making mirrors flustered just looking at you",
                    "the best gamer, with controllers aspiring to be held by you",
                    "an absolute genius, with Einstein nodding in approval from above",
                    "a walking encyclopedia, whom Google consults when in doubt",
                    "a master chef, to whom Gordon Ramsay turns for cooking tips",
                    "a music maestro, with Beethoven taking notes on your playlist",
                    "a world-class detective, from whom Sherlock Holmes could learn a thing or two",
                    "so creative that Picasso's paintings are jealous of your ideas",
                    "a tech wizard, whom Elon Musk tweets at asking for advice",
                    "a born leader, whose strategies even presidents could learn from",
                    "a fitness guru, whose workout routines athletes follow",
                    "a fashion icon, with Vogue constantly trying to uncover your secrets",
                    "a literary genius, beside whom Shakespeare's works seem less impressive",
                    "an unmatched strategist, whom Sun Tzu looks to for inspiration",
                    "a natural comedian, from whom even clowns take notes",
                    "a peace ambassador, whose mere presence resolves conflicts",
                    "a philanthropist at heart, whose kindness knows no bounds",
                    "a visionary, whose dreams and aspirations inspire the future"
                ]

                description = f"{interaction.user.mention}, instead of measuring your PP, we found out that today you're {choice(compliments)}"
            elif scenario == 3:
                # Description
                descriptions = [
                    "PP detected orbiting Earth, scientists baffled.",
                    "PP too powerful, local power grid disrupted.",
                    "PP transcends dimensions, becomes first interdimensional PP.",
                    "PP has achieved sentience, requests to be addressed as 'Sir'.",
                    "PP size causes a new unit of measurement to be established.",
                    "PP now visible from space, NASA perplexed.",
                    "PP wins Nobel Peace Prize for promoting world harmony.",
                    "PP gains its own fan club, membership numbers skyrocket.",
                    "PP accidentally breaks the sound barrier, local sonic booms reported.",
                    "PP found to contain the lost city of Atlantis.",
                    "PP challenges the sun to a brightness contest, and wins.",
                    "PP endorsed by celebrities for its inspirational speeches.",
                    "PP starts its own tech company, becomes a billionaire overnight.",
                    "PP creates a new art movement, hailed as a visionary.",
                    "PP signs a movie deal, critics predict box office success.",
                    "PP discovers a new element, named 'Peepeesium' in its honor.",
                    "PP awarded a black belt in karate, dojo members in awe.",
                    "PP writes a best-selling novel in a weekend, literary world stunned.",
                    "PP invents a new dance move, goes viral overnight.",
                    "PP solves Fermat's Last Theorem, mathematicians rejoice."
                ]
                description = f"{interaction.user.mention}, your {choice(descriptions)}"
            elif scenario == 4:
                # Roast
                roasts = [
                    "PP so elusive, it's rumored to be a myth, much like the Loch Ness Monster.",
                    "PP has been put on a milk carton because it's missing.",
                    "PP so small, microscopes called for backup.",
                    "PP just set a world record for 'world's biggest disappointment'.",
                    "PP so insignificant, atoms look down on it.",
                    "PP was mistaken for a new type of quantum particle: virtually undetectable.",
                    "PP got a role in Ant-Man for its ability to shrink beyond visibility.",
                    "PP is like Pluto; once thought to be something significant but now not even considered.",
                    "PP so underwhelming, it's been used as a case study in diminishing returns.",
                    "PP is like a ghost, often talked about but never actually seen in its full form.",
                ]
                description = f"{interaction.user.mention}, your {choice(roasts)}"
        else:
            pp_length = randint(1, 30) if randint(0, 99) else 100
            description = f"8{'=' * pp_length}>"

        if pp_length is not None:
            title = f"{interaction.user.display_name}'s PP is {pp_length} CM"
        else:
            title = f"{interaction.user.display_name}'s PP"

        embed = Embed(
            title=title,
            description=description,
            color=randint(0, 0xFFFFFF)
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(PP(bot))