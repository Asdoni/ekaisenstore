from discord import app_commands, Interaction, Colour, Member, Embed
from discord.ext import commands
import re
import aiohttp
import asyncio
from PIL import Image
from io import BytesIO

from bot import EGirlzStoreBot

class RoleCreator(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    async def convert_image_to_png(self, url):
        print(f"Attempting to fetch image from URL: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"HTTP Response Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.read()
                    try:
                        image = Image.open(BytesIO(data))
                        png_image = BytesIO()
                        image.save(png_image, format='PNG')
                        png_image.seek(0)
                        print("Image conversion to PNG successful.")
                        return png_image
                    except Exception as e:
                        print(f"Failed to convert image to PNG: {e}")
                        return None
                else:
                    print("Failed to fetch image from URL.")
                    return None


    @app_commands.command(
        name="set_role_icon",
        description="Sets or updates the icon of a custom role."
    )
    async def set_role_icon(self, interaction: Interaction, emoji: str):
        await interaction.response.defer(ephemeral=False)

        colour = Colour.default()
        role_name = " "
        custom_emoji_pattern = r'<a?:\w+:\d+>'

        if not re.match(custom_emoji_pattern, emoji):
            await interaction.followup.send("Please use a valid existing custom emoji. Standard Discord emojis are not supported for role icons.", ephemeral=True)
            return

        row = await self.bot.db.fetchone("SELECT role_id FROM custom_role WHERE user_id = $1 AND guild_id = $2", interaction.user.id, interaction.guild_id)
        role = None
        creating_new_role = False

        if row:
            role_id = row[0]
            role = interaction.guild.get_role(role_id)
            if role is None:
                creating_new_role = True
        else:
            creating_new_role = True

        for r in interaction.user.roles:
            if r.permissions.administrator or r.permissions > interaction.guild.default_role.permissions:
                if r.icon:
                    await interaction.followup.send("You already have a role with higher permissions and an icon. You cannot use this command.", ephemeral=True)
                    return

        if emoji and "ROLE_ICONS" in interaction.guild.features:
            match = re.search(r'<a?:\w+:(\d+)>', emoji)
            if match:
                emoji_id = match.group(1)
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
                image_data = await self.convert_image_to_png(emoji_url)

                if image_data:
                    image_data.seek(0)
                    target_position = max(len(interaction.guild.roles) - 4, 1)
                    image_size = len(image_data.read())
                    print(f"Converted PNG size: {image_size} bytes")
                    image_data.seek(0)
                    
                    if creating_new_role:
                        role = await interaction.guild.create_role(name=role_name, colour=colour, reason="Custom role creation with emoji", display_icon=image_data.read())
                        action = 'Created'
                        try:
                            existing_row = await self.bot.db.fetchone("SELECT role_id FROM custom_role WHERE user_id = $1 AND guild_id = $2", interaction.user.id, interaction.guild_id)
                            if existing_row:
                                await self.bot.db.execute("UPDATE custom_role SET role_id = $1 WHERE user_id = $2", role.id, interaction.user.id)
                            else:
                                await self.bot.db.execute("INSERT INTO custom_role (user_id, role_id, guild_id) VALUES ($1, $2, $3)", interaction.user.id, role.id, interaction.guild_id)
                            print(f"Successfully added role {role.id} for user {interaction.user.id} to the database.")
                        except Exception as e:
                            print(f"Failed to add role to database: {e}")
                    else:
                        await role.edit(reason="Custom role icon update with emoji", display_icon=image_data.read())
                        action = 'Updated'

                    original_position = role.position
                    await asyncio.sleep(1)
                    await role.edit(position=target_position)
                    print(f"Role '{role.name}' moved from position {original_position} to {target_position}.")

                    try:
                        await interaction.user.add_roles(role)
                        print(f"Role '{role.name}' successfully assigned to {interaction.user.name}.")
                    except Exception as e:
                        print(f"Failed to assign role: {e}")
                else:
                    await interaction.response.send_message("Failed to retrieve emoji for role icon.", ephemeral=True)
                    return
            else:
                await interaction.response.send_message("You must provide an emoji to set as the role icon.", ephemeral=True)
                return
            
        title = f"Custom Role Icon {action}"
        description = f"**{action}** a custom icon role for {interaction.user.mention} with the chosen emoji!"
        footer_text = "Role Management | EGirlzStore Bot"
        embed = Embed(title=title, colour=colour, description=description)
        embed.set_thumbnail(url=emoji_url)
        embed.set_footer(text=footer_text, icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        await self.bot.db.execute("DELETE FROM custom_role WHERE user_id = $1", member.id)
        print(f"Deleted custom role data for user {member.id} from the database.")

    @app_commands.command(
        name="delete_role",
        description="Deletes your custom role."
    )
    async def delete_role(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        
        row = await self.bot.db.fetchone("SELECT role_id FROM custom_role WHERE user_id = $1 AND guild_id = $2", interaction.user.id, interaction.guild_id)
        if row:
            role_id = row[0]
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await role.delete()
                    await self.bot.db.execute("DELETE FROM custom_role WHERE user_id = $1", interaction.user.id)
                    await interaction.followup.send("Your custom role has been deleted.", ephemeral=True)
                except Exception as e:
                    print(f"Exception during role deletion or database operation: {e}")
                    await interaction.followup.send("There was an issue deleting your custom role. Please try again later.", ephemeral=True)
            else:
                print("Role not found in the guild or already deleted.")
                await interaction.followup.send("Error: Role not found or already deleted.", ephemeral=True)
        else:
            print("User does not have a custom role according to the database.")
            await interaction.followup.send("You do not have a custom role to delete.", ephemeral=True)

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(RoleCreator(bot))
