import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import random
import io
import aiohttp

class Love(commands.Cog):    
    def __init__(self, bot):        
        self.bot = bot
            
    async def fetch_avatar(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()

    @app_commands.command( 
        name="love",
        description="Compare your love"       
    )
    async def love(self, ctx, user: discord.User):
        # Check if the user is the same as the command invoker
        if user == ctx.user:
            embed = discord.Embed(title="NSFW WARNING", description="It's fine to love yourself but do not overdo it, especially here in public.", color=0xFF69B4)
            await ctx.response.send_message(embed=embed)
            return  # Stop further processing

        percentage = random.randint(0, 100)
        love_image = self.get_love_image(percentage)

        # Determine avatar URLs
        author_avatar_url = str(ctx.user.avatar.url) if ctx.user.avatar else str(ctx.user.default_avatar.url)
        user_avatar_url = str(user.avatar.url) if user.avatar else str(user.default_avatar.url)

        # Fetching avatars
        author_avatar = await self.fetch_avatar(author_avatar_url)
        user_avatar = await self.fetch_avatar(user_avatar_url)

        AVATAR_SIZE = (128, 128)
        LOVE_IMG_SIZE = (AVATAR_SIZE[0] // 2, AVATAR_SIZE[1] // 2)
    
        # Check for avatars, if not available use default
        author_avatar_url = str(ctx.user.avatar.url) if ctx.user.avatar else ctx.user.default_avatar_url
        user_avatar_url = str(user.avatar.url) if user.avatar else str(user.default_avatar.url)
    
        # Converting to Images and resizing
        author_image = Image.open(io.BytesIO(author_avatar)).resize(AVATAR_SIZE)
        user_image = Image.open(io.BytesIO(user_avatar)).resize(AVATAR_SIZE)

        # Open and resize the love image
        love_img = Image.open(love_image).resize(LOVE_IMG_SIZE)

        # Determine the max height
        max_height = max(author_image.height, user_image.height, love_img.height)

        # Adjust the positions
        author_img_y = (max_height - author_image.height) // 2
        user_img_y = (max_height - user_image.height) // 2
        love_img_y = (max_height - love_img.height) // 2

        # Create the final image
        total_width = author_image.width * 2  # Just twice the width of an avatar
        new_img = Image.new('RGB', (total_width, max_height))

        # Paste the author and user images first
        new_img.paste(author_image, (0, author_img_y))
        new_img.paste(user_image, (author_image.width, user_img_y))

        # Adjust the X-coordinate for love_img to center it between the avatars
        love_img_x = (total_width - love_img.width) // 2

        # Paste the love_img in the center
        new_img.paste(love_img, (love_img_x, love_img_y), mask=love_img)

        # Convert image to bytes for sending in discord
        with io.BytesIO() as buffer:
            new_img.save(buffer, format='PNG')
            buffer.seek(0)
            discord_file = discord.File(fp=buffer, filename='love.png')
        
        # Embed Creation
        embed = discord.Embed(title=f"Love Percentage: {percentage}%", color=0xFF69B4)
        embed.set_image(url="attachment://love.png")

        # Set the footer text
        footer_text = f"Love from {ctx.user.display_name} to {user.display_name}"
        embed.set_footer(text=footer_text)

        await ctx.response.send_message(file=discord_file, embed=embed)

    def get_love_image(self, percentage):
        # Determine which image to use based on percentage
        if percentage == 100:
            return "cogs/Love/images/love_10.png"
        elif percentage >= 90:
            return "cogs/Love/images/love_9.png"
        elif percentage >= 80:
            return "cogs/Love/images/love_8.png"
        elif percentage >= 70:
            return "cogs/Love/images/love_7.png"
        elif percentage >= 60:
            return "cogs/Love/images/love_6.png"
        elif percentage >= 50:
            return "cogs/Love/images/love_5.png"
        elif percentage >= 40:
            return "cogs/Love/images/love_4.png"
        elif percentage >= 30:
            return "cogs/Love/images/love_3.png"
        elif percentage >= 20:
            return "cogs/Love/images/love_2.png"
        else:
            return "cogs/Love/images/love_1.png"
        
def setup(bot):    
    bot.add_cog(Love(bot))