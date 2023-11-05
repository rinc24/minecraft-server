#!/usr/bin/env python
from main import telebot, bot, update_data, get_data, os, re
from mctools import RCONClient

rcon = RCONClient(os.getenv("RCON_HOST", "127.0.0.1"))
assert rcon.login(os.getenv("RCON_PASSWORD")), "Нет связи с RCON"


def run_command(cmd: str):
    response = rcon.command(cmd)
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", response)


def check_admin(handler):
    def wrapper(message):
        admin_user_id = get_data()["ADMIN_USER_ID"]

        # print(f"check_admin | {handler.__name__} | ADMIN_USER_ID: {admin_user_id} | user.id: {message.from_user.id}")
        if admin_user_id == message.from_user.id:
            return handler(message)

    return wrapper


def check_chat(handler):
    def wrapper(message):
        chat_id = get_data()["CHAT_ID"]

        # print(f"check_chat | {handler.__name__} | CHAT_ID: {chat_id} | chat.id: {message.chat.id}")
        if chat_id == message.chat.id:
            return handler(message)

    return wrapper


@bot.message_handler(commands=["itsmebro"])
def itsmebro(message):
    update_data(ADMIN_USER_ID=message.from_user.id)
    bot.reply_to(message, f"`ADMIN_USER_ID:` {message.from_user.id}")


@bot.message_handler(commands=["here"])
@check_admin
def here(message):
    update_data(CHAT_ID=message.chat.id)
    bot.reply_to(message, f"`CHAT_ID:` {message.chat.id}\nУведомления будут приходить в этот чат.")


@bot.message_handler(commands=["sync"])
@check_chat
def sync(message):
    new_value = not get_data()["SYNC_CHAT"]
    update_data(SYNC_CHAT=new_value)
    bot.reply_to(message, "Все сообщения в чате " + ("" if new_value else "НЕ ") + "синхронизируются с сервером.")


@bot.message_handler(commands=["players"])
@check_chat
def players(message):
    bot.reply_to(message, run_command("list"))


@bot.message_handler(func=lambda m: True)
@check_chat
def all_mesages(message):
    message_text = message.text.strip()

    if not message_text or not get_data()["SYNC_CHAT"]:
        return

    chat_member = bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)

    author = chat_member.custom_title or ""

    if not author:
        author = message.from_user.username or " ".join(
            [name for name in (message.from_user.first_name, message.from_user.last_name) if name]
        )

    run_command(f"say <{author}>: {message_text}")


bot.set_my_commands(
    [
        telebot.types.BotCommand("/players", "Список игроков"),
        telebot.types.BotCommand("/sync", "Синхронизировать чат"),
    ]
)

if __name__ == "__main__":
    bot.infinity_polling()
