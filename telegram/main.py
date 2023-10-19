#!/usr/bin/env python
import os
import re
import json
from time import sleep
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN", "6503031622:AAGK5icKtOWCw1rtEnU5zdxAdfcVkNXw44M")
LATEST_LOG_PATH = os.getenv("LATEST_LOG_PATH", "/opt/minecraft-server/minecraft-data/logs/latest.log")
PROCESSED_LOG_PATH = os.getenv("PROCESSED_LOG_PATH", "./processed.log")
PATTERN = r"^\[(\d{2}:\d{2}:\d{2})\] \[Server thread\/(\w{4})\]: (\[Not Secure\] )?(.*)$"
DEFAULT_CONFIG = {"ADMIN_CHAT_ID": None, "CHAT_ID": None}


def get_config():
    with open("config.json", "r+") as config_file:
        config_file_content = config_file.read()

        config = dict(**DEFAULT_CONFIG)

        print(config_file_content)

        if not config_file_content:
            config_file.write(json.dumps(config, ensure_ascii=False, indent=2))
        else:
            config.update(json.loads(config_file_content))
        return config


def write_config(config):
    _config = get_config()
    _config.update(config)
    with open("config.json", "w+") as config_file:
        config_file.write(json.dumps(_config, ensure_ascii=False, indent=2))


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MARKDOWN")

last_log_size = 0

while __name__ == "__main__":
    try:
        chat_id = get_config()["CHAT_ID"]
        actual_log_size = os.path.getsize(LATEST_LOG_PATH)

        if not chat_id or last_log_size == actual_log_size:
            sleep(1)
            continue
        else:
            last_log_size = actual_log_size

        with open(LATEST_LOG_PATH, "r") as latest_log:
            latest_log_lines = latest_log.readlines()

        with open(PROCESSED_LOG_PATH, "a+") as processed_log:
            processed_log_lines = processed_log.readlines()
            last_processed_log_line = processed_log_lines[-1] if processed_log_lines else None
            start_index = latest_log_lines.index(last_processed_log_line) + 1 if last_processed_log_line else 0

            messages = []
            for latest_log_line in latest_log_lines[start_index:]:
                processed_log.write(latest_log_line)

                match = re.match(PATTERN, latest_log_line)

                if not match:
                    continue

                groups = match.groups()

                time = groups[0]
                log_level = groups[1]
                message = groups[3]

                if log_level == "INFO":
                    messages.append(f"`{time}`\t{message}")

            if messages:
                bot.send_message(chat_id, "\n".join(messages), disable_notification=True)

    except Exception as e:
        print(e)
