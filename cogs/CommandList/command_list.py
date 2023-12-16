import os

from discord import app_commands, Interaction, Embed
from discord.ext import commands

from bot import EGirlzStoreBot


class CommandList(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.command(
        name="command-list",
        description="Get a list of all commands organized by category"
    )
    async def list_commands(self, interaction: Interaction):
        cogs_dict = {}

        # text commands
        for cog in self.bot.cogs.values():
            cogs_dict[cog.qualified_name] = [cmd for cmd in cog.get_commands() if not getattr(cmd, 'hidden', False)]

        # slash commands
        for cmd in self.bot.tree.get_commands():
            if not getattr(cmd, 'hidden', False):
                if cmd.binding and hasattr(cmd.binding, 'qualified_name'):
                    cog_name = cmd.binding.qualified_name
                else:
                    cog_name = 'No Category'
                if cog_name not in cogs_dict:
                    cogs_dict[cog_name] = []
                cogs_dict[cog_name].append(cmd)

        embed = Embed(
            title=f":star2: {self.bot.user.display_name} Commands :star2:",
            description="Here are all the commands available!",
            color=0x4CAF50  # Green color
        )

        for cog_name, cmds in sorted(cogs_dict.items()):
            command_descriptions = []
            for cmd in cmds:
                prefix = '/' if isinstance(cmd, app_commands.Command) else os.getenv('PREFIX')
                description = getattr(cmd, 'description', 'No description provided.')
                command_descriptions.append(f"{prefix}{cmd.name}{' - '+description if description else ''}")

            command_list = "\n".join(command_descriptions)
            if command_list:
                # Split the command list if it's too long for one field
                embed.add_field(name=f"Commands for {cog_name}", value=command_list[:1024], inline=False)
                if len(command_list) > 1024:
                    remaining_text = command_list[1024:]
                    embed.add_field(name=f"More {cog_name} Commands", value=remaining_text[:1024], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(CommandList(bot))