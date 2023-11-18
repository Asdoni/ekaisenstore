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
    async def peepee(self, ctx): 
        random_color = random.randint(0, 0xFFFFFF)
        bb_not_found = False
        triple_boob = False
        random_length = None  # Initialize to None
        cup_size = "Unknown"  # Initialize cup_size
        
        if ctx.user.id == 209748857683312640:
            random_length = 10
        else:
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
            # You can adjust how many spaces you want here
            spaces = (' ' + '\u200B') * 4
            triple_line = f"({spaces}.{spaces})({spaces}.{spaces})({spaces}.{spaces})\n"

            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s boobies are special!", 
                description=triple_line,
                color=random_color
            )
            embed.set_thumbnail(url=ctx.user.avatar.url)
            await ctx.response.send_message(embed=embed)
        else:
            # Calculate the number of spaces
            num_spaces = random_length * 2 # If you want 7 spaces, just set it to random_length, no need to multiply by 2

            # Build the string representation for the boobies
            spaces = (' ' + '\u200B') * num_spaces  # This should add the appropriate number of spaces
            boob_line = f"({spaces}.{spaces})({spaces}.{spaces})\n"

            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s boobies are {cup_size} cup!", 
                description=boob_line,  # Set the boob_line string as description
                color=random_color
            )
            embed.set_thumbnail(url=ctx.user.avatar.url)
            await ctx.response.send_message(embed=embed)

def setup(bot):    
    bot.add_cog(BB(bot))
