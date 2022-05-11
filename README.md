# Автоматическое поднятие резюме в поиске на hh.ru

Раз в ~4 часа находим все активные резюме и поднимаем их вверх в поиске 
:hand_over_mouth:

Это домашний проект, а я ищу работу.

**Настройка и запуск:**
1. Для отправки уведомлений об успешном/неуспешном обновлении резюме в 
   Telegram:
   
    В `app/__init__.py` в классе `Settings` изменить 
   `telegram_logging` на `True` (по ум.)
   _(Может работать некорректно, но со своей задачей справляется)_

2. Переименовать `.env.dev` в `.env` и заполнить значения:
   - `HH_EMAIL_LOGIN` - Логин (email или телефон)
   - `HH_PASSWORD` - Пароль от аккаунта
   
   Если `telegram_logging == True`, то:
   - `TG_API_KEY` - Токен к боту для уведомлений
   - `TG_CHAT_ID` - Ваш Telegram ID (узнать - [@username_to_id_bot](https://t.me/username_to_id_bot))

3. Собираем контейнер с помощью **Docker-compose** и запускаем:
    ```shell
   docker-compose -f {path}/docker-compose.yaml up -d
    ```
4. Разместить на своём сервере можно:
    ```shell
   docker save <image_id> | bzip2 | pv | ssh user@host docker load
   ```

**Special thanks:**
- https://github.com/SergeyPirogov/webdriver_manager
- https://nander.cc/using-selenium-within-a-docker-container
