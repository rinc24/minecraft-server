#!/usr/bin/env python
from main import bot, write_config, get_config


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


bot.infinity_polling()
