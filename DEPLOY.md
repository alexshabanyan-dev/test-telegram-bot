# Инструкция по развертыванию на сервере

## Шаг 1: Подключение к серверу

```bash
ssh root@92.53.96.141
```

Или если используется другой пользователь:

```bash
ssh ваш_пользователь@92.53.96.141
```

## Шаг 2: Установка зависимостей

После подключения выполните:

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Python и необходимых инструментов
apt install -y python3 python3-pip python3-venv git

# Проверка версии Python (должна быть 3.7+)
python3 --version
```

## Шаг 3: Клонирование репозитория

```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем репозиторий
git clone https://github.com/alexshabanyan-dev/test-telegram-bot.git

# Переходим в директорию проекта
cd test-telegram-bot
```

## Шаг 4: Настройка окружения

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

## Шаг 5: Настройка конфигурации

```bash
# Создаем файл .env из примера
cp .env.example .env

# Редактируем .env файл (нужен nano или vim)
nano .env
```

Заполните файл `.env`:

```
API_ID=39080865
API_HASH=52627a516d14534b43359a277b758c03
CHANNEL_NAME=@vmestesilamoscow
```

Сохраните файл: `Ctrl+O`, затем `Enter`, затем `Ctrl+X`

## Шаг 6: Первый запуск (для авторизации)

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Запускаем бота для авторизации
python main.py
```

Введите:

1. Номер телефона (с кодом страны, например: +79055355604)
2. Код подтверждения из Telegram
3. Пароль 2FA (если включен) или просто Enter

После успешной авторизации остановите бота: `Ctrl+C`

## Шаг 7: Настройка автозапуска через systemd

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/telegram-monitor.service
```

Вставьте следующее содержимое:

```ini
[Unit]
Description=Telegram Channel Monitor Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/test-telegram-bot
Environment="PATH=/root/test-telegram-bot/venv/bin"
ExecStart=/root/test-telegram-bot/venv/bin/python /root/test-telegram-bot/main.py
Restart=always
RestartSec=30
# Увеличиваем время ожидания перед перезапуском
StartLimitInterval=300
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
```

**Важно:** Если вы используете другого пользователя (не root), замените `/root` на путь к домашней директории этого пользователя.

Сохраните файл и выполните:

```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable telegram-monitor.service

# Запускаем сервис
sudo systemctl start telegram-monitor.service

# Проверяем статус
sudo systemctl status telegram-monitor.service
```

## Полезные команды для управления

```bash
# Проверить статус бота
sudo systemctl status telegram-monitor.service

# Посмотреть логи
sudo journalctl -u telegram-monitor.service -f

# Остановить бота
sudo systemctl stop telegram-monitor.service

# Запустить бота
sudo systemctl start telegram-monitor.service

# Перезапустить бота
sudo systemctl restart telegram-monitor.service

# Отключить автозапуск
sudo systemctl disable telegram-monitor.service
```

## Обновление кода

Если вы обновили код в репозитории:

```bash
cd ~/test-telegram-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart telegram-monitor.service
```

## Устранение проблем

### Ошибка "database is locked"

Если бот постоянно перезапускается с ошибкой "database is locked":

```bash
# Запустите скрипт исправления
cd ~/test-telegram-bot
bash fix_session_lock.sh

# Или вручную:
sudo systemctl stop telegram-monitor.service
pkill -f "python.*main.py" || true
rm -f ~/test-telegram-bot/*.session-journal
sudo systemctl start telegram-monitor.service
```

### Обновление systemd сервиса

Если обновили файл `telegram-monitor.service`:

```bash
sudo cp ~/test-telegram-bot/telegram-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart telegram-monitor.service
```

## Проверка работы

Бот должен работать постоянно. Проверьте логи:

```bash
sudo journalctl -u telegram-monitor.service -n 50
```

Если видите сообщения о подключении и мониторинге - все работает!
