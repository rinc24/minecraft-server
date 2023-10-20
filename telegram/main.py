#!/usr/bin/env python
import os
import re
import json
from time import sleep
from pathlib import Path
import telebot


BOT_TOKEN = os.getenv("BOT_TOKEN")

LATEST_LOG_PATH = Path(os.getenv("LATEST_LOG_PATH", "logs/latest.log"))
PROCESSED_LOG_PATH = Path(os.getenv("PROCESSED_LOG_PATH", "logs/processed.log"))
DATA_PATH = Path(os.getenv("DATA_PATH", "data/data.json"))

DEFAULT_DATA = {"ADMIN_USER_ID": None, "CHAT_ID": None, "SYNC_CHAT": True}

PATTERN = r"^\[(\d{2}:\d{2}:\d{2})\] \[Server thread\/(\w{4})\]: (\[Not Secure\] )?(.*)$"


def get_data():
    if not os.path.isfile(DATA_PATH):
        write_data(DEFAULT_DATA)

    with open(DATA_PATH, "r") as data_file:
        data_file_content = data_file.read()

        data = dict(**DEFAULT_DATA)

        if not data_file_content:
            write_data(data)
        else:
            data.update(json.loads(data_file_content))
        return data


def write_data(data):
    with open(DATA_PATH, "w") as data_file:
        data_file.write(json.dumps(data, ensure_ascii=False, indent=2))


def update_data(**kwargs):
    data = get_data()
    data.update(kwargs)
    write_data(data)


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MARKDOWN")

last_log_size = 0

while __name__ == "__main__":
    chat_id = get_data()["CHAT_ID"]
    actual_log_size = os.path.getsize(LATEST_LOG_PATH)

    if not chat_id or last_log_size == actual_log_size:
        sleep(1)
        continue
    else:
        last_log_size = actual_log_size

    LATEST_LOG_PATH.touch()
    PROCESSED_LOG_PATH.touch()

    with open(LATEST_LOG_PATH, "r") as latest_log:
        latest_log_lines = [line.strip() for line in latest_log.read().split("\n") if line.strip()]

    with open(PROCESSED_LOG_PATH, "r") as processed_log:
        processed_log_lines = [line.strip() for line in processed_log.read().split("\n") if line.strip()]
        last_processed_log_line = processed_log_lines[-1] if processed_log_lines else None

    with open(PROCESSED_LOG_PATH, "w") as processed_log:
        start_index = -20
        if last_processed_log_line and last_processed_log_line in latest_log_lines:
            start_index = len(latest_log_lines) - (latest_log_lines[::-1].index(last_processed_log_line))

        messages = []
        new_latest_log_lines = latest_log_lines[start_index:]
        processed_log.write("\n".join(processed_log_lines + new_latest_log_lines))

        for latest_log_line in new_latest_log_lines:
            match = re.match(PATTERN, latest_log_line)

            if not match:
                continue

            groups = match.groups()

            time = groups[0]
            log_level = groups[1]
            message = groups[3]

            if log_level == "INFO" and "[Rcon]" not in message:
                messages.append(f"`{time}`\t{message}")

        if messages:
            bot.send_message(chat_id, "\n".join(messages), disable_notification=True)
