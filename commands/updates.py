import discord 
from discord import app_commands
from discord.ext import commands
from config import VERSION

class Updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="update-log", description="View the latest update log.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.user.id))
    async def updates(
        self,
        interaction: discord.Interaction,
    ):
        embed = discord.Embed(
            title=f"Latest Update Log for {VERSION}",
            description=f"View the latest update log [here](https://github.com/ARC-UCF/AR-CAT-UCF/releases)!\n\nAll related updates and issues for AR-CAT will be posted on the GitHub and handled on the GitHub page!",
            color=discord.Color.blue(),
        )
        
        embed.set_footer(text=f"{VERSION}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @updates.error
    async def updates_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Command On Cooldown!",
                description=f"Please wait {error.retry_after:.2f} seconds before trying to use this command again.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
async def setup(bot):
    await bot.add_cog(Updates(bot))