from discord.ext import commands # type: ignore
from googletrans import Translator # type: ignore

class Translation(commands.Cog):
    """Translation commands for translating text."""

    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    @commands.command()
    async def translate(self, ctx, target_language: str, *, text: str):
        """Translate text to the target language. (<prefix>translate <target_language> <text>)"""
        try:
            # Translate the text and await the result
            translated = await self.translator.translate(text, dest=target_language)
            await ctx.send(f"Original: {text}\nTranslated ({target_language}): {translated.text}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Translation(bot))
