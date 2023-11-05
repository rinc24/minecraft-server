Сервер был поднят по
[статье](https://www.howtoforge.com/how-to-install-spigot-minecraft-server-on-ubuntu-20-04/).

Для запуска создать файл `.env` с двумя переменными:

```env
BOT_TOKEN="6503031622:AAGK5icK***********zdxAdfcVkNXw44M"
RCON_PASSWORD=f03e6e3*******36324e7b
```

`BOT_TOKEN` -- токен телеграм-бота у [@BotFather](https://t.me/BotFather)

`RCON_PASSWORD` -- Пароль админ-консоли сервера, появляется после запуска
сервера. Получить:

```shell
cat /home/minecraft/server/server.properties | grep "rcon.password="
```
