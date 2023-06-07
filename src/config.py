# region imports <- This is foldable

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests

# endregion

exts = [
    "cogs.coc",
]

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


class Bot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix, intents=intents, **kwargs)

    async def on_ready(self):
        for ext in exts:
            await self.load_extension(ext)
        print("loaded all cogs")

        synced = await self.tree.sync()
        print(f"synced {len(synced)} commands")

        print("Bot is ready")


if __name__ == "__main__":
    bot = Bot(command_prefix=">", intents=discord.Intents.all())
    bot.run(token)
