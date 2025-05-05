import discord
import requests # type: ignore
from discord.ext import commands # type: ignore
import random

# Ganti dengan API key Rawg Video Games Database yang sudah kamu dapatkan
API_KEY = "YOUR_RAWG_API_KEY"
BASE_URL = "https://api.rawg.io/api/games"
OMDB_API_KEY = "YOUR_OMDB_API"
OMDB_BASE_URL = "http://www.omdbapi.com/"

class Information(commands.Cog):
    """Information commands including jokes and fun facts."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        """Send a random joke."""
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()
        await ctx.send(f"{joke['setup']} - {joke['punchline']}")

    @commands.command()
    async def fact(self, ctx):
        """Send a random fun fact."""
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        fact = response.json()
        await ctx.send(f"Fun Fact: {fact['text']}")

    @commands.command()
    async def game(self, ctx):
        """Send a random information about a game per day."""
        try:
            params = {
                'key': API_KEY,  # API Key dari Rawg
                'page_size': 1,  # Mengambil 1 game secara acak
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if data['results']:
                game = data['results'][0]
                game_name = game['name']
                game_description = game.get('description_raw', game.get('short_description', 'No description available.'))

                if game_description == 'No description available.':
                    released = game.get('released', 'Release date not available.')
                    platforms = ', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])
                    genres = ', '.join([genre['name'] for genre in game.get('genres', [])])
                    game_description = f"Released: {released}\nPlatforms: {platforms}\nGenres: {genres}"

                game_facts = [
                    f"Did you know? {game_name} was released in {game.get('released', 'Unknown date')}. {game_description}",
                    f"Here’s a fun fact: {game_name} - Did you know it’s available on {', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])}? {game_description}",
                    f"Fun fact about {game_name}: {game_description}. It has been a fan favorite across multiple platforms!"
                ]
                fact = random.choice(game_facts)
                await ctx.send(fact)
            else:
                await ctx.send("Could not retrieve a game fact. Try again later.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error: {e}")

    @commands.command()
    async def recommend(self, ctx, year: int):
        """Recommend games based on a specific year. (<prefix>recommend <year>)"""
        try:
            params = {
                'key': API_KEY,
                'page_size': 5,  # Fetch 5 games
                'dates': f'{year}-01-01,{year}-12-31',  # Filter by year
                'ordering': '-rating',  # Sort by rating
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if data['results']:
                game = data['results'][0]
                game_name = game['name']
                rating = game['rating']
                release_date = game.get('released', 'Release date not available.')
                platforms = ', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])
                genres = ', '.join([genre['name'] for genre in game.get('genres', [])])

                game_info = (
                    f"**Recommended Game with the Highest Rating based on {year}:** {game_name}\n"
                    f"Rating: {rating}/5\n"
                    f"Released: {release_date}\n"
                    f"Platforms: {platforms}\n"
                    f"Genres: {genres}"
                )
                await ctx.send(game_info)
            else:
                await ctx.send(f"No recommended game found for the year {year}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error: {e}")

    @commands.command(name='movie')
    async def get_movie_info(self, ctx, *, movie_name: str):
        """Get information about a movie from OMDb. (<prefix>movie <movie_name>)"""
        url = f"{OMDB_BASE_URL}?t={movie_name}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data['Response'] == 'False':
            await ctx.send(f"Movie not found: {movie_name}")
            return

        title = data.get('Title', 'N/A')
        year = data.get('Year', 'N/A')
        rated = data.get('Rated', 'N/A')
        released = data.get('Released', 'N/A')
        runtime = data.get('Runtime', 'N/A')
        genre = data.get('Genre', 'N/A')
        director = data.get('Director', 'N/A')
        writer = data.get('Writer', 'N/A')
        actors = data.get('Actors', 'N/A')
        plot = data.get('Plot', 'N/A')
        language = data.get('Language', 'N/A')
        country = data.get('Country', 'N/A')
        awards = data.get('Awards', 'N/A')
        poster = data.get('Poster', 'N/A')
        imdb_rating = data.get('imdbRating', 'N/A')
        imdb_votes = data.get('imdbVotes', 'N/A')
        imdb_id = data.get('imdbID', 'N/A')

        embed = discord.Embed(title=title, description=plot, color=0x00ff00)
        embed.set_thumbnail(url=poster)
        embed.add_field(name="Year", value=year, inline=True)
        embed.add_field(name="Rated", value=rated, inline=True)
        embed.add_field(name="Released", value=released, inline=True)
        embed.add_field(name="Runtime", value=runtime, inline=True)
        embed.add_field(name="Genre", value=genre, inline=True)
        embed.add_field(name="Director", value=director, inline=True)
        embed.add_field(name="Writer", value=writer, inline=True)
        embed.add_field(name="Actors", value=actors, inline=True)
        embed.add_field(name="Language", value=language, inline=True)
        embed.add_field(name="Country", value=country, inline=True)
        embed.add_field(name="Awards", value=awards, inline=True)
        embed.add_field(name="IMDB Rating", value=imdb_rating, inline=True)
        embed.add_field(name="IMDB Votes", value=imdb_votes, inline=True)
        embed.add_field(name="IMDB ID", value=imdb_id, inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Information(bot))
