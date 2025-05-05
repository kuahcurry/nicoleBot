import discord
from discord.ext import commands
import asyncio

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the intent to read message content

# Dictionary to store prefixes for each server
prefixes = {}

def get_prefix(bot, message):
    guild_id = message.guild.id if message.guild else None
    return prefixes.get(guild_id, '.')

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# Load extensions
initial_extensions = [
    'functions.music',
    'functions.information',
    'functions.notes',
    'functions.weather',
    'functions.translation',
    'functions.server_stats',
    'functions.games',
    'functions.random_number'
]

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")
    try:
        await bot.load_extension('handlers.extension_handler')
        print("Loaded handler extension.")
    except Exception as e:
        print(f"Failed to load handler extension: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("Commands registered:")
    for command in bot.commands:
        print(f"- {command.name}")

@bot.event
async def on_message(message):
    print(f"Received message: {message.content}")
    await bot.process_commands(message)  # Ensure commands are processed

@bot.command(name='setprefix')
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, prefix: str):
    """Set a custom prefix for the server."""
    prefixes[ctx.guild.id] = prefix
    await ctx.send(f"Prefix set to: {prefix}")

@bot.command(name='getprefix')
async def get_prefix_command(ctx):
    """Get the current prefix for the server."""
    prefix = prefixes.get(ctx.guild.id, '.')
    await ctx.send(f"The current prefix is: '{prefix}'")

async def main():
    await load_extensions()
    await bot.start('YOUR_DISCORD_BOT_TOKEN')

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is not None:
        await member.edit(mute=False, deafen=True)  # Deafen bot when joining a voice channel

if __name__ == '__main__':
    asyncio.run(main())
