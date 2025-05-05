import yt_dlp as youtube_dl # type: ignore
from discord.ext import commands # type: ignore
from discord import FFmpegPCMAudio # type: ignore
import requests # type: ignore
import asyncio

# Dictionary to store song queues for each server
song_queues = {}

class Music(commands.Cog):
    """Music commands for managing songs and playback."""

    def __init__(self, bot):
        self.bot = bot
        self.current_song_titles = {}  # Dictionary to store current song titles for each server

    @commands.command()
    async def join(self, ctx):
        """Join the voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                await channel.connect()
                await ctx.send(f"Connected to {channel.name}!")
            except Exception as e:
                await ctx.send(f"Failed to connect: {e}")
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("I am not connected to a voice channel.")

    @commands.command()
    async def play(self, ctx, *, song_name):
        """Play a song or add it to the queue. (<prefix>play <song_name>)"""
        if not ctx.voice_client:
            await ctx.send("I am not connected to a voice channel.")
            return

        await ctx.send(f"Searching for: {song_name}...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'default_search': 'ytsearch',
            'extractor-retries': 5,
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{song_name}", download=False)
                video_info = info_dict['entries'][0]
                video_url = video_info['url']
                video_title = video_info['title']
                audio_url = None

                for format in video_info['formats']:
                    if 'url' in format and ('acodec' in format and format['acodec'] != 'none'):
                        audio_url = format['url']
                        break

                if audio_url:
                    guild_id = str(ctx.guild.id)
                    if guild_id not in song_queues:
                        song_queues[guild_id] = []

                    song_queues[guild_id].append({
                        'name': video_title,
                        'url': audio_url
                    })
                    position = len(song_queues[guild_id])
                    await ctx.send(f"Added to queue at position {position}: {video_title}")

                    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                        self.current_song_titles[guild_id] = video_title
                        await self.play_next(ctx)
                else:
                    await ctx.send("No suitable audio stream found.")
        except Exception as e:
            await ctx.send(f"Error while processing the song: {e}")
            print(f"Error: {e}")

    async def play_next(self, ctx):
        """Play the next song in the queue."""
        guild_id = str(ctx.guild.id)
        if guild_id in song_queues and song_queues[guild_id]:
            song = song_queues[guild_id].pop(0)
            self.current_song_titles[guild_id] = song['name']
            await ctx.send(f"Now playing: {song['name']}")

            audio_source = FFmpegPCMAudio(song['url'], **{
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            })

            def after_playing(error):
                if error:
                    print(f"Error occurred: {error}")
                coro = self.play_next(ctx)
                asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

            ctx.voice_client.stop()
            ctx.voice_client.play(audio_source, after=after_playing)
        else:
            self.current_song_titles[guild_id] = None
            await ctx.send("No more songs in the queue.")

    @commands.command()
    async def pause(self, ctx):
        """Pause the current song."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("No music is playing.")

    @commands.command()
    async def resume(self, ctx):
        """Resume the paused song."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.send("The music is not paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the current song and clear the queue."""
        guild_id = str(ctx.guild.id)
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            if guild_id in song_queues:
                song_queues[guild_id].clear()
        else:
            await ctx.send("No music is playing.")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
        else:
            await ctx.send("No music is playing.")

    @commands.command()
    async def queue(self, ctx):
        """Show the current song queue."""
        guild_id = str(ctx.guild.id)
        if guild_id in song_queues and song_queues[guild_id]:
            queue_message = "\n".join(
                [f"{i + 1}. {song['name']}" for i, song in enumerate(song_queues[guild_id])]
            )
            await ctx.send(f"Current queue:\n{queue_message}")
        else:
            await ctx.send("The queue is empty.")

    @commands.command()
    async def song(self, ctx):
        """Display the current playing song."""
        guild_id = str(ctx.guild.id)
        if guild_id in self.current_song_titles and self.current_song_titles[guild_id]:
            await ctx.send(f"Now playing: {self.current_song_titles[guild_id]}")
        else:
            await ctx.send("No music is currently playing.")

    @commands.command()
    async def lyrics(self, ctx):
        """Get the lyrics of the currently playing song."""
        guild_id = str(ctx.guild.id)
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("No song is currently playing.")
            return

        song_name = self.current_song_titles.get(guild_id)
        if not song_name:
            await ctx.send("No song is currently playing.")
            return

        parts = song_name.split(" - ")

        if len(parts) < 2:
            await ctx.send("Sorry, the song format is incorrect.")
            return

        artist, title = parts
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"

        try:
            async with ctx.typing():
                response = requests.get(url, timeout=5)
            data = response.json()

            if 'lyrics' in data:
                lyrics = data['lyrics'].replace('\n\n', '\n').strip()
                await ctx.send(f"Lyrics for {song_name}:\n{lyrics}")
            else:
                await ctx.send(f"Lyrics for {song_name} isn't available.")
        except requests.exceptions.Timeout:
            await ctx.send("Request timed out.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Music(bot))