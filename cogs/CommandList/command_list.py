import discord
from discord import app_commands, Embed
from discord.ext import commands

from bot import EGirlzStoreBot

class CommandList(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    async def send_embeds(self, interaction: discord.Interaction, embeds):
        for embed in embeds:
            await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="command-list",
        description="Get a list of all commands organized by category"
    )
    async def list_commands(self, interaction: discord.Interaction):
        cogs_dict = {}

        for cog in self.bot.cogs.values():
            cogs_dict[cog.qualified_name] = [cmd for cmd in cog.get_commands() if not getattr(cmd, 'hidden', False)]

        for cmd in self.bot.tree.get_commands():
            if not getattr(cmd, 'hidden', False):
                if cmd.binding and hasattr(cmd.binding, 'qualified_name'):
                    cog_name = cmd.binding.qualified_name
                else:
                    cog_name = 'No Category'
                if cog_name not in cogs_dict:
                    cogs_dict[cog_name] = []
                cogs_dict[cog_name].append(cmd)

        embeds = []
        embed = Embed(title=f":star2: {self.bot.user.display_name} Commands :star2:", 
                      description="Here are all the commands available!",
                      color=0x4CAF50)
        
        for cog_name, cmds in sorted(cogs_dict.items()):
            command_descriptions = [f"/{cmd.name} - {getattr(cmd, 'description', 'No description provided.')}"
                                    for cmd in cmds]

            command_list = "\n".join(command_descriptions)
            if command_list:
                if len(embed.fields) >= 25:
                    embeds.append(embed)
                    embed = Embed(title=f"Continued: {self.bot.user.display_name} Commands",
                                  color=0x4CAF50)

                embed.add_field(name=f"Commands for {cog_name}", value=command_list[:1024], inline=False)
                if len(command_list) > 1024:
                    remaining_text = command_list[1024:]
                    embed.add_field(name=f"More {cog_name} Commands", value=remaining_text[:1024], inline=False)

        embeds.append(embed)
        await interaction.response.send_message(embed=embeds[0], ephemeral=False)
        await self.send_embeds(interaction, embeds[1:])

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(CommandList(bot))