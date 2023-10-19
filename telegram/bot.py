#!/usr/bin/env python
from main import telebot, bot, write_config, get_config
import subprocess


def run_command(cmd: str, long_arg: str = None) -> str:
    command = "docker exec -i minecraft rcon-cli".split()
    command.append(cmd)
    if long_arg:
        command.append(long_arg)
    return subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True).stdout


def check_admin(message):
    return get_config()["ADMIN_USER_ID"] == message.from_user.id


def check_chat(message):
    return get_config()["CHAT_ID"] == message.chat.id


@bot.message_handler(commands=["itsmebro"])
def itsmebro(message):
    write_config({"ADMIN_USER_ID": message.from_user.id})
    bot.reply_to(message, f"`ADMIN_USER_ID:` {message.from_user.id}")


@bot.message_handler(commands=["here"], func=check_admin)
def here(message):
    write_config({"CHAT_ID": message.chat.id})
    bot.reply_to(message, f"`CHAT_ID:` {message.chat.id}\nУведомления будут приходить в этот чат.")


@bot.message_handler(commands=["sync"], func=check_chat)
def sync(message):
    new_value = not get_config()["SYNC_CHAT"]
    write_config({"SYNC_CHAT": new_value})
    bot.reply_to(message, "Все сообщения в чате " + ("" if new_value else "НЕ ") + "синхронизируются с сервером.")


@bot.message_handler(commands=["players"], func=check_chat)
def players(message):
    bot.reply_to(message, run_command("list"))


@bot.message_handler(func=check_chat)
def all_mesages(message):
    message_text = message.text.strip()

    if not message_text or not get_config()["SYNC_CHAT"]:
        return

    chat_member = bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)

    author = chat_member.custom_title or ""

    if not author:
        author = message.from_user.username or " ".join(
            [name for name in (message.from_user.first_name, message.from_user.last_name) if name]
        )

    run_command("say", f"<{author}>: {message_text}")


bot.set_my_commands(
    [
        telebot.types.BotCommand("/players", "Список игроков"),
        telebot.types.BotCommand("/sync", "Синхронизировать чат"),
    ]
)

while __name__ == "__main__":
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)
