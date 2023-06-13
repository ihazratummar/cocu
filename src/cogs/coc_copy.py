import discord
from discord.ext import commands, tasks
from config import Bot
from dotenv import load_dotenv
import requests
import os
import tracemalloc
import json

tracemalloc.start()
load_dotenv()

COC_API_TOKEN = os.getenv("COC_API")
# Clan tag
CLAN_TAG = "%2328R0L9RUR"
CHANNEL_ID = 874162166343815229
GLOBAL_CHANNEL_ID = 1118004962044166235

PREVIOUS_DATA_FILE = "previous_data.json"


class Coc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_token = COC_API_TOKEN
        self.clan_tag = CLAN_TAG
        self.previous_members = {}
        self.total_troops_donated = {}
        self.total_trophies = {}

        self.load_previous_data()
        self.check_member_status.start()
        print("Background task started.")

    def load_previous_data(self):
        if os.path.exists(PREVIOUS_DATA_FILE):
            with open(PREVIOUS_DATA_FILE, "r") as file:
                self.previous_members = json.load(file)

                for member_tag, member in self.previous_members.items():
                    if "name" in member:
                        player_name = member["name"]
                        self.total_trophies[player_name] = member["trophies"]

    def save_previous_data(self):
        with open(PREVIOUS_DATA_FILE, "w") as file:
            json.dump(self.previous_members, file)

    @tasks.loop()
    async def check_member_status(self):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        }

        url = f"https://api.clashofclans.com/v1/clans/{self.clan_tag}/members"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching clan members: {e}")
            return

        current_members = {member["tag"]: member for member in data["items"]}

        for member_tag, member in current_members.items():
            if member_tag not in self.previous_members:
                self.previous_members[member_tag] = {
                    "trophies": member["trophies"],
                    "donations": member["donations"],
                }
                continue

            previous_member = self.previous_members[member_tag]

            if member["trophies"] > previous_member["trophies"]:
                trophies_diff = member["trophies"] - previous_member["trophies"]
                await self.send_trophy_increase_notification(
                    member["tag"], member["name"], trophies_diff
                )

            if member["donations"] > previous_member["donations"]:
                donations_diff = member["donations"] - previous_member["donations"]
                await self.send_donation_notification(
                    member["tag"], member["name"], donations_diff
                )

            previous_member["trophies"] = member["trophies"]
            previous_member["donations"] = member["donations"]

        self.save_previous_data()

    async def send_trophy_increase_notification(
        self, player_tag, player_name, trophies_diff
    ):
        channel = self.bot.get_channel(CHANNEL_ID)

        if channel is not None:
            if player_name not in self.total_trophies:
                self.total_trophies[player_tag] = self.previous_members[player_tag][
                    "trophies"
                ]

            self.total_trophies[player_tag] += trophies_diff
            total_trophies = self.total_trophies[player_tag]

            message = f"🏆 Congratulations `{player_name}` for increasing trophies by `{trophies_diff}`! Total trophies: `{total_trophies}`"
            await channel.send(message)

    async def send_donation_notification(self, player_tag, player_name, donations_diff):
        channel = self.bot.get_channel(CHANNEL_ID)

        if channel is not None:
            if player_tag not in self.total_troops_donated:
                self.total_troops_donated[player_tag] = self.previous_members[
                    player_tag
                ]["donations"]

            self.total_troops_donated[player_tag] += donations_diff
            total_donations = self.total_troops_donated[player_tag]

            message = f"💪 `{player_name}` donated `{donations_diff}` troops! Total donated `{total_donations}`"
            await channel.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Coc(bot))
    print("Cog added.")
