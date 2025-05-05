import discord # type: ignore
from discord.ext import commands # type: ignore

class ServerStats(commands.Cog):
    """Commands to display server statistics."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo')
    async def server_info(self, ctx):
        """Displays information about the server."""
        try:
            guild = ctx.guild
            embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
            embed.add_field(name="Server ID", value=guild.id, inline=True)
            embed.add_field(name="Owner", value=guild.owner, inline=True)
            embed.add_field(name="Preferred Locale", value=guild.preferred_locale, inline=True)
            embed.add_field(name="Member Count", value=guild.member_count, inline=True)
            embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
            embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
            embed.set_thumbnail(url=guild.icon.url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred while fetching server info: {e}")
            print(f"Error in server_info command: {e}")

async def setup(bot):
    await bot.add_cog(ServerStats(bot))