import discord # type: ignore
from discord.ext import commands # type: ignore
import requests # type: ignore

# Ganti dengan API key OpenWeatherMap yang valid
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *, location):
        """Showing the weather in a specific location. (<prefix>weather <location>)"""
        try:
            # Membuat URL API dengan parameter lokasi dan API_KEY
            complete_url = f"{BASE_URL}q={location}&appid={API_KEY}&units=metric"
            response = requests.get(complete_url)
            data = response.json()

            # Cek apakah respons API mengandung kode 'cod' dan apakah nilainya 404 (bukan ditemukan)
            if data.get("cod") != 200:
                await ctx.send(f"Location '{location}' not found. Please check the spelling.")
                return

            # Jika data ditemukan, lanjutkan
            main_data = data["main"]
            weather_data = data["weather"][0]
            temperature = main_data["temp"]
            pressure = main_data["pressure"]
            humidity = main_data["humidity"]
            description = weather_data["description"]
            weather_report = f"Weather in {location.capitalize()}:\n"
            weather_report += f"Temperature: {temperature}°C\n"
            weather_report += f"Pressure: {pressure} hPa\n"
            weather_report += f"Humidity: {humidity}%\n"
            weather_report += f"Description: {description.capitalize()}"
            await ctx.send(weather_report)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error: {e}")

# Fungsi untuk setup cog
async def setup(bot):
    await bot.add_cog(Weather(bot))
