import discord
from discord.ext import commands
from discord import app_commands
import random

# Create a dictionary for cup sizes
cup_sizes = {
    1: "AA",
    2: "A",
    3: "B",
    4: "C",
    5: "D",
    6: "E",
    7: "F",
    8: "G",
    9: "H",
    10: "I"
}

class BB(commands.Cog):    
    def __init__(self, bot):        
        self.bot = bot

    @app_commands.command(     
        name="bb",     
        description="Measure your boobies" 
    )
    async def boobies(self, ctx): 
        random_color = random.randint(0, 0xFFFFFF)
        bb_not_found = False
        triple_boob = False
        random_length = None  # Initialize to None
        cup_size = "Unknown"  # Initialize cup_size

        if random.randint(1, 100) <= 3.5:
            bb_not_found = True
        else:
            special_chance = random.randint(1, 100)
            if special_chance == 1:
                triple_boob = True  
            else:
                random_length = random.randint(1, 10)
        
        # Move this block here, after setting random_length
        if random_length is not None:
            cup_size = cup_sizes.get(random_length, "Unknown")

        if bb_not_found:
            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s bb", 
                description=f"<:smolpp:1062443373165822022> I'm sorry {ctx.user.mention}, you are flat! <:smolpp:1062443373165822022>", 
                color=random_color
            )
        elif triple_boob:
            spaces = (' ' + '\u200B') * 4
            triple_line = f"({spaces}.{spaces})({spaces}.{spaces})({spaces}.{spaces})\n"

            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s boobies are special!", 
                description=triple_line,
                color=random_color
            )
        else:
            num_spaces = random_length * 2 
            spaces = (' ' + '\u200B') * num_spaces
            boob_line = f"({spaces}.{spaces})({spaces}.{spaces})\n"

            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s boobies are {cup_size} cup!", 
                description=boob_line,
                color=random_color
            )

        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)

def setup(bot):    
    bot.add_cog(BB(bot))
