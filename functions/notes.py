from discord.ext import commands # type: ignore
from google.cloud import firestore
import os
import json
from dotenv import load_dotenv # type: ignore

load_dotenv()

class Notes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if credentials_json:
            credentials_dict = json.loads(credentials_json)
            self.db = firestore.Client.from_service_account_info(credentials_dict)
        else:
            raise ValueError("Google application credentials not found in environment variables")

    @commands.command()
    async def write(self, ctx, name: str, *, content: str):
        """Write a note with a specific name. (<prefix>write <title> <content>)"""
        guild_id = str(ctx.guild.id)
        doc_ref = self.db.collection('servers').document(guild_id).collection('notes').document(name)
        if doc_ref.get().exists:
            await ctx.send(f"A note with the name '{name}' already exists. Use a different name or delete the existing note.")
        else:
            doc_ref.set({'content': content})
            await ctx.send(f"Note '{name}' saved!")

    @commands.command()
    async def view(self, ctx, name: str):
        """View the content of a note by its name. (<prefix>view <title>)"""
        guild_id = str(ctx.guild.id)
        doc_ref = self.db.collection('servers').document(guild_id).collection('notes').document(name)
        doc = doc_ref.get()
        if doc.exists:
            await ctx.send(f"**{name}:**\n{doc.to_dict()['content']}")
        else:
            await ctx.send(f"No note found with the name '{name}'.")

    @commands.command()
    async def delete(self, ctx, name: str):
        """Delete a note by its name. (<prefix>delete <title>)"""
        guild_id = str(ctx.guild.id)
        doc_ref = self.db.collection('servers').document(guild_id).collection('notes').document(name)
        if doc_ref.get().exists:
            doc_ref.delete()
            await ctx.send(f"Note '{name}' deleted.")
        else:
            await ctx.send(f"No note found with the name '{name}'.")

    @commands.command()
    async def lists(self, ctx):
        """List all the notes available."""
        guild_id = str(ctx.guild.id)
        notes_ref = self.db.collection('servers').document(guild_id).collection('notes')
        docs = notes_ref.stream()
        notes_list = [doc.id for doc in docs]
        if notes_list:
            await ctx.send(f"Here are your notes:\n" + "\n".join(notes_list))
        else:
            await ctx.send("You have no notes.")

async def setup(bot):
    await bot.add_cog(Notes(bot))