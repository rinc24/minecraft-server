#!/usr/bin/env python
import os
import re
import json
from time import sleep
import telebot


BOT_TOKEN = os.getenv("BOT_TOKEN")
LATEST_LOG_PATH = os.getenv("LATEST_LOG_PATH", "latest.log")
PROCESSED_LOG_PATH = os.getenv("PROCESSED_LOG_PATH", "processed.log")
PATTERN = r"^\[(\d{2}:\d{2}:\d{2})\] \[Server thread\/(\w{4})\]: (\[Not Secure\] )?(.*)$"
DEFAULT_DATA = {"ADMIN_USER_ID": None, "CHAT_ID": None, "SYNC_CHAT": True}


def get_data():
    with open("data.json", "w+") as data_file:
        data_file_content = data_file.read()

        data = dict(**DEFAULT_DATA)

        if not data_file_content:
            data_file.write(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            data.update(json.loads(data_file_content))
        return data


def write_data(data):
    _data = get_data()
    _data.update(data)
    with open("data.json", "w+") as data_file:
        data_file.write(json.dumps(_data, ensure_ascii=False, indent=2))


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MARKDOWN")

last_log_size = 0

while __name__ == "__main__":
    try:
        chat_id = get_data()["CHAT_ID"]
        actual_log_size = os.path.getsize(LATEST_LOG_PATH)

        if not chat_id or last_log_size == actual_log_size:
            sleep(1)
            continue
        else:
            last_log_size = actual_log_size

        with open(LATEST_LOG_PATH, "r") as latest_log:
            latest_log_lines = [line.strip() for line in latest_log.read().split("\n") if line.strip()]

        with open(PROCESSED_LOG_PATH, "r") as processed_log:
            processed_log_lines = [line.strip() for line in processed_log.read().split("\n") if line.strip()]
            last_processed_log_line = processed_log_lines[-1] if processed_log_lines else None

        with open(PROCESSED_LOG_PATH, "w") as processed_log:
            start_index = 0
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

    except Exception as e:
        print(e)
