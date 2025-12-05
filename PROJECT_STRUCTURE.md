# Структура проекта

```
telegram-bot/
├── main.py                    # Основной скрипт бота
├── config.py                  # Конфигурация (ключевые слова)
├── requirements.txt           # Зависимости Python
├── README.md                  # Основная документация
├── .env.example              # Пример конфигурации
├── .gitignore                # Игнорируемые файлы
├── telegram-monitor.service   # Systemd service файл
│
├── scripts/                   # Вспомогательные скрипты
│   ├── check_bot_status.sh   # Проверка статуса бота
│   ├── check_channel.py      # Проверка доступности канала
│   ├── debug_bot.sh          # Полная диагностика
│   ├── fix_session_lock.sh   # Исправление блокировок сессии
│   ├── force_restart_bot.sh  # Принудительный перезапуск
│   ├── get_chat_id.py        # Получение chat_id
│   ├── setup_server.sh       # Автоматическая настройка сервера
│   ├── test_monitor.py       # Тестовый скрипт для отладки
│   └── view_logs.sh          # Удобный просмотр логов
│
└── docs/                      # Документация
    ├── DEPLOY.md             # Инструкции по развертыванию
    ├── SETUP_BOT.md          # Настройка бота
    └── CLEANUP.md            # Документация по очистке
```

## Использование скриптов

Все скрипты находятся в папке `scripts/`. Для запуска используйте:

```bash
# Из корня проекта
bash scripts/check_bot_status.sh

# Или из папки scripts
cd scripts
bash check_bot_status.sh
```

## Документация

- `README.md` - основная документация и быстрый старт
- `docs/DEPLOY.md` - подробные инструкции по развертыванию на сервере
- `docs/SETUP_BOT.md` - настройка бота для отправки уведомлений
- `docs/CLEANUP.md` - информация об очистке проекта

