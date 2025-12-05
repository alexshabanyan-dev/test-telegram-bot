#!/bin/bash

# Принудительный перезапуск бота с очисткой

echo "🔄 Принудительный перезапуск бота..."
echo ""

# 1. Останавливаем сервис
echo "1️⃣  Останавливаем сервис..."
sudo systemctl stop telegram-monitor.service
sleep 2

# 2. Убиваем все процессы Python связанные с ботом
echo "2️⃣  Останавливаем все процессы Python..."
pkill -9 -f "python.*main.py" || true
pkill -9 -f "python.*test_monitor" || true
sleep 2

# 3. Удаляем файлы блокировки
echo "3️⃣  Удаляем файлы блокировки..."
cd ~/test-telegram-bot
rm -f *.session-journal
rm -f telegram_monitor.session-journal
rm -f test_monitor_session.session-journal

# 4. Проверяем, что процессы остановлены
echo "4️⃣  Проверяем процессы..."
if pgrep -f "python.*main.py" > /dev/null; then
    echo "   ⚠️  Процессы все еще запущены, убиваем принудительно..."
    pkill -9 -f "python.*main.py"
    sleep 1
fi

# 5. Запускаем сервис
echo "5️⃣  Запускаем сервис..."
sudo systemctl start telegram-monitor.service
sleep 3

# 6. Проверяем статус
echo "6️⃣  Статус сервиса:"
sudo systemctl status telegram-monitor.service --no-pager -l | head -15
echo ""

# 7. Показываем последние логи
echo "7️⃣  Последние логи (последние 30 строк):"
sudo journalctl -u telegram-monitor.service -n 30 --no-pager
echo ""

echo "✅ Готово! Теперь смотрите логи в реальном времени:"
echo "   sudo journalctl -u telegram-monitor.service -f"
