Raise your resume on [HeadHunter](https://hh.ru/) :see_no_evil:
=
Автоматическое поднятие всех резюме в поиске с уведомлением в Telegram
-

> Это домашний проект, а я ищу работу.

### Настройка и запуск:

1. **Для отправки сообщений в Telegram о результатах обновления 
   резюме**:
   
    В `app/settings.py` в классе `Settings` изменить 
   `telegram_logging` на `True`<br>
   _(Может работать некорректно, но со своей задачей справляется)_<br><br>

2. **Переименовать `.env.dev` в `.env` и заполнить значения**:
   - `HH_EMAIL_LOGIN` - Логин (email или телефон)
   - `HH_PASSWORD` - Пароль от аккаунта
   <br><br>
   Если `telegram_logging == True`, то:
   - `TG_API_KEY` - Токен к боту для уведомлений (создать - 
     [@BotFather](https://t.me/botfather))
   - `TG_CHAT_ID` - Ваш Telegram ID (узнать - [@username_to_id_bot](https://t.me/username_to_id_bot))

   <br>
3. **Собираем контейнер с помощью `Docker-compose`**:
    ```shell
   docker-compose -f {path}/docker-compose.yaml up -d
    ```
    <br>
4. **Настроим автоматический запуск Docker контейнера с помощью `systemd service`**:
<br><br>
   - Создадим конфигурационный файл ([docs](https://docs.fedoraproject.org/en-US/quick-docs/understanding-and-administering-systemd/index.html)):
   
     ```shell
     nano /etc/systemd/system/hh_resume_raising.service
     ```
   - Скопируйте и сохраните:
     ```ini
     [Unit]
     Description=HeadHunter Resume Raising Container
     After=network.target
     After=docker.service
     Requires=docker.service
     Wants=hh_resume_raising.timer
   
     [Service]
     Type=simple
     TimeoutStartSec=0
     Restart=on-failure
     ExecStartPre=-/usr/bin/docker stop hh_resume_raising
     # ExecStartPre=-/usr/bin/docker rm hh_resume_raising
     ExecStart=/usr/bin/docker start hh_resume_raising
   
     [Install]
     WantedBy=multi-user.target
     ```
   - Перезагружаем файлы служб, чтобы включить наш сервис:
     ```shell
     systemctl daemon-reload
     ```
   - Запускаем нашу службу и активируем её запуск во время загрузки:
     ```shell
     systemctl start hh_resume_raising.service
   
     systemctl enable hh_resume_raising.service
     ```
   - Проверяем состояние, чтобы убедиться, что служба создана и была запущена:
     ```shell
     systemctl status hh_resume_raising.service
   
     # Вывод
     ○ hh_resume_raising.service - HeadHunter Resume Raising Container
          Loaded: loaded (/etc/systemd/system/hh_resume_raising.service; disabled; vendor preset: enabled)
          Active: inactive (dead)
   
     Jun 28 10:03:08 your_pc_name systemd[1]: Starting HeadHunter Resume Raising 
     Container...
     Jun 28 10:03:08 your_pc_name docker[4017546]: hh_resume_raising
     Jun 28 10:03:08 your_pc_name systemd[1]: Started HeadHunter Resume Raising 
     Container.
     Jun 28 10:03:09 your_pc_name docker[4017568]: hh_resume_raising
     Jun 28 10:03:09 your_pc_name systemd[1]: hh_resume_raising.service: 
     Deactivated 
     successfully.
     ```
   - Создадим таймер для запуска службы по "расписанию":
     ```shell
     nano /etc/systemd/system/hh_resume_raising.timer
     ```
   - Копируем и сохраняем. В разделе `Timer` вы 
     можете изменить желаемые интервалы обновлений (при изменении важно 
     знать, что запуск будет происходить в интервале до +15 минут):
     ```shell
     [Unit]
     Description=HeadHunter Resume Raising Container
     Requires=hh_resume_raising.service
   
     [Timer]
     Unit=hh_resume_raising.service
     AccuracySec=900sec
     OnCalendar=*-*-* 07:30:00
     OnCalendar=*-*-* 10:45:00
     OnCalendar=*-*-* 15:50:00
     OnCalendar=*-*-* 19:15:00
     # OnCalendar=*-*-* 23:30:00
     Persistent=true
   
     [Install]
     WantedBy=timers.target
     ```
   - Устанавливаем запуск таймера при загрузке:
     ```shell
     systemctl enable hh_resume_raising.timer
     ```
   **После всех проделанных шагов, служба запускается с помощью таймера. Если же 
необходимо запустить её вручную**:
   ```shell
   systemctl start hh_resume_raising.service
   ```

### Разместить на своём сервере можно:
```shell
docker save $(docker images --filter=reference="headhunter*" -q) | bzip2 | pv | ssh user@host docker load
```

## Special thanks:
- https://github.com/SergeyPirogov/webdriver_manager
- https://nander.cc/using-selenium-within-a-docker-container
- https://github.com/AlanAndre/HHResumeUpdater
