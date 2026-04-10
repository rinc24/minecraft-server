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

Использование autossh (Рекомендуется)
autossh — это утилита, которая специально создана для мониторинга SSH-туннелей. Если связь обрывается, она мгновенно перезапускает SSH.

1. Установите её:
   1. `sudo apt update && sudo apt install autossh -y`
   2. Запустите туннель через неё: `autossh -M 0 -f -N -q -o "ServerAliveInterval 60" -o "ServerAliveCountMax 3" -D 0.0.0.0:1488 serb`
       * -M 0: отключает собственный мониторинг портов autossh (рекомендуется полагаться на встроенные в SSH ServerAlive).
       * ServerAliveInterval 60: каждые 60 секунд проверять, жив ли сервер.
       * ServerAliveCountMax 3: если 3 проверки подряд не прошли — перезапустить туннель.
