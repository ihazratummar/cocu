import json
import os

PREVIOUS_FILE = ".previous_data.json"


def load_previous_data():
    if not file_exists():
        return {}

    with open(PREVIOUS_FILE, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}

    return data


def save_previous_data(data):
    with open(PREVIOUS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def file_exists():
    return os.path.exists(PREVIOUS_FILE)
