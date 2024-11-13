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
        admin_user_ids = get_data()["ADMIN_USER_IDS"]

        if message.from_user.id in admin_user_ids:
            return handler(message)
        else:
            bot.reply_to(message, "Команда доступна только:\n" + get_list_admins(message.chat.id))

    return wrapper


def check_chat(handler):
    def wrapper(message):
        chat_id = get_data()["CHAT_ID"]

        if chat_id == message.chat.id:
            return handler(message)

    return wrapper


@bot.message_handler(commands=["itsmebro"])
def itsmebro(message):
    admin_user_ids = set(get_data()["ADMIN_USER_IDS"])

    if message.from_user.id in admin_user_ids:
        admin_user_ids -= {message.from_user.id}
    else:
        admin_user_ids |= {message.from_user.id}

    update_data(ADMIN_USER_IDS=list(admin_user_ids))
    bot.reply_to(message, get_list_admins(chat_id=message.chat.id))
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except:
        pass


@bot.message_handler(commands=["here"])
@check_admin
def here(message):
    update_data(CHAT_ID=message.chat.id)
    bot.reply_to(message, f"`CHAT_ID:` {message.chat.id}\nУведомления будут приходить в этот чат.")


@bot.message_handler(commands=["sync"])
@check_admin
def sync(message):
    new_value = not get_data()["SYNC_CHAT"]
    update_data(SYNC_CHAT=new_value)
    bot.reply_to(message, "Все сообщения в чате " + ("" if new_value else "НЕ ") + "синхронизируются с сервером.")


@bot.message_handler(commands=["rcon"])
@check_admin
def rcon_handler(message):
    command = message.text.strip("/").strip().removeprefix("rcon").strip()
    bot.reply_to(message, run_command(command))


@bot.message_handler(commands=["players"])
@check_chat
def players(message):
    bot.reply_to(message, run_command("list"))


@bot.message_handler(commands=["day"])
@check_admin
@check_chat
def day(message):
    bot.reply_to(message, run_command("gamerule doDaylightCycle false"))
    bot.reply_to(message, run_command("time 60"))

@bot.message_handler(commands=["night"])
@check_admin
@check_chat
def night(message):
    bot.reply_to(message, run_command("gamerule doDaylightCycle true"))
    bot.reply_to(message, run_command("time set 6000"))

def get_list_admins(chat_id: int):
    return "\n".join(
        [f"* {get_chat_member_name(chat_id, user_id=admin_id)}" for admin_id in get_data()["ADMIN_USER_IDS"]]
    ) or "Нет админов"


@bot.message_handler(commands=["admins"])
@check_chat
def admins(message):
    bot.reply_to(message, get_list_admins(message.chat.id))


def get_chat_member_name(chat_id: int, user_id: int):
    chat_member = bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    return (
            chat_member.custom_title
            or chat_member.user.username
            or " ".join([name for name in (chat_member.user.first_name, chat_member.user.last_name) if name])
    )


@bot.message_handler(func=lambda m: True)
@check_chat
def all_mesages(message):
    message_text = message.text.strip()

    if not message_text or not get_data()["SYNC_CHAT"]:
        return

    author = get_chat_member_name(chat_id=message.chat.id, user_id=message.from_user.id)
    run_command(f"say <{author}>: {message_text}")


bot.set_my_commands(
    [
        telebot.types.BotCommand("/players", "Список игроков"),
        # telebot.types.BotCommand("/admins", "Список админов"),
        # telebot.types.BotCommand("/rcon", "Отправить rcon-команду"),
        telebot.types.BotCommand("/day", "Остановить течение времени"),
        telebot.types.BotCommand("/night", "Включить течение времени"),
        # telebot.types.BotCommand("/sync", "Синхронизировать чат"),
    ]
)

if __name__ == "__main__":
    bot.polling()
