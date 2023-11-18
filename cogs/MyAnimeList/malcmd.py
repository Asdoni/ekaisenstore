import discord
from discord.ext import commands


class MALcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='malcmd', aliases=['helpc', 'hcom'], brief='Show a list of available commands for MyAnimeList.', description='Shows a list of all available commands and their usage.')
    async def MALcmd(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="MyAnimeList Command List:", color=0x8a7bff)

        embed.add_field(name="Character Info:", value="Get information about a character from an anime or manga.\nUsage: `$character <name>` or `$char <name>`\nExample: `$character Mikasa Ackerman` or `$char Oreki Houtarou`", inline=False)
        
        embed.add_field(name="Character Images:", value="Fetch images for a character from an anime or manga.\nUsage: `$images <name>`, `$image <name>`, or `$im <name>`\nExample: `$images Mikasa Ackerman`, `$image Lelouch`, or `$im Eru Chitanda`", inline=False)
        
        embed.add_field(name="Anime Info:", value="Get information about an anime.\nUsage: `$anime <name>`\nExample: `$anime Hyouka`, `$anime NHK ni Youkoso!`", inline=False)
        
        embed.add_field(name="Manga Info:", value="Get information about a manga.\nUsage: `$manga <name>`\nExample: `$manga Omniscient Reader`, `$manga attack on titan`", inline=False)
        
        embed.set_footer(text="Note: Some commands have aliases for shorter usage.")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MALcmd(bot))
