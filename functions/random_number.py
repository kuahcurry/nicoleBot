import discord
from discord.ext import commands
import random
import asyncio

class RandomNumber(commands.Cog):
    """Commands to generate random numbers and shuffle inputs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='random')
    async def random_number(self, ctx, max_number: int):
        """Generate a random number between 1 and the specified max number. (<prefix>random <max_number>)"""
        if max_number < 1:
            await ctx.send("Please provide a number greater than 0.")
            return

        random_num = random.randint(1, max_number)
        await ctx.send(f"Random number between 1 and {max_number} = '{random_num}'")

    @commands.command(name='shuffle')
    async def shuffle_input(self, ctx, *, items: str):
        """Shuffle and randomly select an item from the provided list. (<prefix>shuffle <item1>, <item2>, ...)"""
        item_list = [item.strip() for item in items.split(',')]
        if len(item_list) < 2:
            await ctx.send("Really? you can't just shuffle 1 item, you dirty #####. So please provide at least two items to shuffle.")
            return

        selected_item = random.choice(item_list)
        
        async with ctx.typing():
            await ctx.send(f"Shuffled Inputs, be ready for anything or anyone to be selected: {', '.join(item_list)}")
        
        async with ctx.typing():
            await asyncio.sleep(2)  # Pause for 2 seconds
            await ctx.send(f"And those who gain the Champion of the Selection of today's challenge is : {selected_item}")

async def setup(bot):
    await bot.add_cog(RandomNumber(bot))