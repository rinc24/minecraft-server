#!/usr/bin/env python
from main import telebot, bot, update_data, get_data, os, re, sleep
from mctools import RCONClient

RCON_HOST = os.getenv("RCON_HOST", "minecraft.server")
RCON_PASSWORD = os.getenv("RCON_PASSWORD")

_rcon = None


def get_rcon():
    global _rcon
    if _rcon is None:
        print(f"RCON: Creating new client for {RCON_HOST}:25575")
        _rcon = RCONClient(RCON_HOST, port=25575)

    try:
        is_auth = _rcon.is_authenticated()
    except:
        is_auth = False

    if not is_auth:
        print(f"RCON: Not authenticated. Logging in...")
        try:
            if not _rcon.login(RCON_PASSWORD):
                print("RCON: Login FAILED (Invalid password?)")
                return None
            print("RCON: Login SUCCESSFUL")
            sleep(0.2)
        except Exception as e:
            print(f"RCON: Connection/Login error: {e}")
            return None

    return _rcon


def run_command(cmd: str):
    global _rcon
    print(f"RCON: Executing command: {cmd}")
    for attempt in range(2):
        rcon = get_rcon()
        if not rcon:
            if attempt == 0:
                print("RCON: First attempt failed, retrying in 0.5s...")
                sleep(0.5)
                continue
            return "Нет связи с RCON (не удалось войти)"

        try:
            response = rcon.command(cmd)
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            return ansi_escape.sub("", response)
        except Exception as e:
            print(f"RCON: Command error on attempt {attempt+1}: {e}")
            if _rcon:
                try:
                    _rcon.stop()
                except:
                    pass
            _rcon = None
            if attempt == 0:
                sleep(0.5)
                continue
            return f"Ошибка RCON: {e}. Попробуйте еще раз."


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
        telebot.types.BotCommand("/sync", "Синхронизировать чат"),
    ]
)

if __name__ == "__main__":
    bot.polling()
