Raise your CV on [HeadHunter](https://hh.ru/) :see_no_evil:
=
Автоматическое поднятие всех резюме в поиске с уведомлением в Telegram
-

Это домашний проект, а я ищу работу.

### Настройка и запуск:

1. Для отправки сообщений в Telegram о результатах обновления 
   резюме:
   
    В `app/settings.py` в классе `Settings` изменить 
   `telegram_logging` на `True`<br>
   _(Может работать некорректно, но со своей задачей справляется)_<br><br>

2. Переименовать `.env.dev` в `.env` и заполнить значения:
   - `HH_EMAIL_LOGIN` - Логин (email или телефон)
   - `HH_PASSWORD` - Пароль от аккаунта
   <br><br>
   Если `telegram_logging == True`, то:
   - `TG_API_KEY` - Токен к боту для уведомлений (создать - 
     [@BotFather](https://t.me/botfather))
   - `TG_CHAT_ID` - Ваш Telegram ID (узнать - [@username_to_id_bot](https://t.me/username_to_id_bot))
   <br><br>
3. Собираем контейнер с помощью **Docker-compose** и запускаем:
    ```shell
   docker-compose -f {path}/docker-compose.yaml up -d --no-start
    ```
4. Разместить на своём сервере можно:
    ```shell
   docker save <image> | bzip2 | pv | ssh user@host docker load
   ```

**Special thanks:**
- https://github.com/SergeyPirogov/webdriver_manager
- https://nander.cc/using-selenium-within-a-docker-container
- https://github.com/AlanAndre/HHResumeUpdater
