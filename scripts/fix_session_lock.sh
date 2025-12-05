#!/bin/bash

# Скрипт для исправления блокировки сессии Telegram
# Использование: bash fix_session_lock.sh

echo "🔧 Исправление блокировки сессии Telegram..."

# Останавливаем сервис
echo "⏹️  Останавливаем сервис..."
sudo systemctl stop telegram-monitor.service

# Ждем завершения процессов
sleep 3

# Убиваем все процессы python, связанные с ботом (если остались)
echo "🧹 Очистка процессов..."
pkill -f "python.*main.py" || true
sleep 2

# Удаляем файлы блокировки сессии
echo "🗑️  Удаление файлов блокировки..."
# Определяем путь к проекту (может быть в разных местах)
PROJECT_DIR=""
if [ -d ~/test-telegram-bot ]; then
    PROJECT_DIR=~/test-telegram-bot
elif [ -d /root/test-telegram-bot ]; then
    PROJECT_DIR=/root/test-telegram-bot
else
    echo "❌ Не удалось найти директорию проекта"
    exit 1
fi
cd "$PROJECT_DIR"

# Удаляем файлы сессии и журналы
rm -f *.session-journal
rm -f telegram_monitor.session-journal

echo "✅ Очистка завершена"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Запустите бота вручную для повторной авторизации (если нужно):"
echo "      source venv/bin/activate"
echo "      python main.py"
echo ""
echo "   2. После успешной авторизации остановите (Ctrl+C) и запустите через systemd:"
echo "      sudo systemctl start telegram-monitor.service"
echo "      sudo systemctl status telegram-monitor.service"
echo ""

