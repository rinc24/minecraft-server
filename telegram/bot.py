#!/usr/bin/env python
from main import bot, write_config, get_config
import subprocess


def run_command(cmd: str, long_arg: str = None) -> str:
    command = "docker exec -i minecraft rcon-cli".split()
    command.append(cmd)
    if long_arg:
        command.append(long_arg)
    return subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True).stdout


@bot.message_handler(commands=["itsmebro"])
def itsmebro(message):
    write_config({"ADMIN_CHAT_ID": message.chat.id})
    bot.reply_to(message, f"`ADMIN_CHAT_ID:` {message.chat.id}")


@bot.message_handler(commands=["here"])
def here(message):
    if get_config()["ADMIN_CHAT_ID"] != message.chat.id:
        return

    write_config({"CHAT_ID": message.chat.id})
    bot.reply_to(message, f"`CHAT_ID:` {message.chat.id}\nУведомления будут приходить в этот чат.")


@bot.message_handler(commands=["players"])
def players(message):
    if get_config()["CHAT_ID"] != message.chat.id:
        return

    bot.reply_to(message, run_command("list"))


@bot.message_handler(commands=["say"])
def say(message):
    if get_config()["CHAT_ID"] != message.chat.id:
        return

    message = message.text.lstrip("/say ")

    if not message:
        return

    run_command("say", message)


bot.infinity_polling()
