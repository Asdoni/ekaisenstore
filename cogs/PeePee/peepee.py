import discord
from discord.ext import commands
from discord import app_commands
import random

class PP(commands.Cog):    
    def __init__(self, bot):        
        self.bot = bot

    @app_commands.command(     
        name="pp",     
        description="Measure your PP" 
    )
    async def peepee(self, ctx): 

        random_color = random.randint(0, 0xFFFFFF)
        pp_not_found = False
        random_length = 0

        # 1/20 chance to set pp_not_found to True
        if random.randint(1, 20) == 1:
            pp_not_found = True
        else:
            special_chance = random.randint(1, 100)
            if special_chance == 1:
                random_length = 100
            else:
                random_length = random.randint(1, 30)  # Generate random number between 1 to 30
        if pp_not_found:
            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s PP", 
                description=f"<:smolPP:1062443373165822022> I'm sorry {ctx.user.mention}, PP not found <:smolPP:1062443373165822022>", 
                color=random_color
            )
        else:
            # Create a string with "=" repeated as many times as random_length
            description_text = "=" * random_length

            embed = discord.Embed(
                title=f"{ctx.user.display_name}'s PP is {random_length} CM", 
                description=f"8{description_text}>",  # Add the repeated "=" string as description
                color=random_color
            )
        # Use display_avatar for the thumbnail in both cases
        embed.set_thumbnail(url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

def setup(bot):    
    bot.add_cog(PP(bot))
