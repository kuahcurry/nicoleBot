from discord.ext import commands # type: ignore

async def setup(bot):  # Tambahkan async
    @bot.command()
    async def load(ctx, extension):
        try:
            await bot.load_extension(f'functions.{extension}')
            await ctx.send(f'Loaded extension: {extension}')
        except Exception as e:
            await ctx.send(f'Error loading extension: {extension}\n{e}')

    @bot.command()
    async def unload(ctx, extension):
        try:
            await bot.unload_extension(f'functions.{extension}')
            await ctx.send(f'Unloaded extension: {extension}')
        except Exception as e:
            await ctx.send(f'Error unloading extension: {extension}\n{e}')

    @bot.command()
    async def reload(ctx, extension):
        try:
            await bot.unload_extension(f'functions.{extension}')
            await bot.load_extension(f'functions.{extension}')
            await ctx.send(f'Reloaded extension: {extension}')
        except Exception as e:
            await ctx.send(f'Error reloading extension: {extension}\n{e}')
