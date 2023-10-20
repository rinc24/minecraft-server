# Стандартный майнкрафт сервер с интеграцией телеграм-бота

Для запуска создать файл `.env`

```env
BOT_TOKEN="6503031622:AAGK5icK***********zdxAdfcVkNXw44M"
RCON_PASSWORD=f03e6e3*******36324e7b
```

`BOT_TOKEN` -- токен телеграм-бота у [@BotFather](https://t.me/BotFather)

`RCON_PASSWORD` -- Пароль админ-консоли сервера, появляется после запуска
сервера. Придется прописать и переподнять. Получить:

```shell
# Поднимаем только сервер
docker-compose up -d minecraft.server
# Получаем сгенерированный пароль
cat minecraft-data/server.properties | grep rcon.password
# Настраиваем две переменные в .env
nano .env
# Поднимаем все остальное
docker-compose up -d
```
