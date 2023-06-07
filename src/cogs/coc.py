import discord
from discord.ext import commands, tasks
from discord import app_commands
from config import Bot
from dotenv import load_dotenv
import requests
import os
import tracemalloc


tracemalloc.start()
load_dotenv()


class Coc(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api_token = os.getenv("COC_API")
        self.clan_tag = "#28R0L9RUR"
        self.previous_members = []

        # Start the background task
        self.check_member_status.start()

    def cog_unload(self):
        # Stop the background task when the cog is unloaded
        self.check_member_status.cancel()

    async def send_notification(self, message):
        channel_id = 874162166343815229  # Replace with your Discord channel ID
        channel = self.bot.get_channel(channel_id)
        if channel:
            print(f"Sending notification: {message}")
            await channel.send(message)
        else:
            print("Channel not found.")

    @tasks.loop(minutes=3)  # Adjust the interval based on your needs
    async def check_member_status(self):
        url = f"https://api.clashofclans.com/v1/clans/%28R0L9RUR/members?limit=2"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                member_data = response.json().get("items", [])
                current_members = [
                    member["tag"]
                    for member in member_data
                    if member["status"] == "online"
                ]
                online_members = list(set(current_members) - set(self.previous_members))
                offline_members = list(
                    set(self.previous_members) - set(current_members)
                )

                if online_members:
                    for member in online_members:
                        await self.send_notification(
                            f"{member} has come online in Clash of Clans."
                        )

                if offline_members:
                    for member in offline_members:
                        await self.send_notification(
                            f"{member} has gone offline in Clash of Clans."
                        )

                self.previous_members = current_members
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching clan members: {e}")

    @check_member_status.before_loop
    async def before_check_member_status(self):
        # Wait for the bot to be ready before starting the background task
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    bot.add_cog(Coc(bot))
