"""
Скрипт для получения вашего chat_id для уведомлений
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из переменных окружения
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

async def get_chat_id():
    """
    Получает chat_id текущего пользователя
    """
    if not API_ID or not API_HASH:
        print("❌ Ошибка: Не указаны API_ID и/или API_HASH в .env файле")
        return
    
    # Инициализируем клиент
    client = TelegramClient('telegram_monitor', API_ID, API_HASH)
    
    try:
        # Подключаемся к Telegram
        await client.start()
        print("✅ Подключение к Telegram установлено\n")
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"👤 Ваш аккаунт: {me.first_name} {me.last_name or ''}")
        print(f"🆔 Ваш user_id: {me.id}")
        print(f"📱 Username: @{me.username}" if me.username else "📱 Username: не установлен")
        
        print("\n" + "="*60)
        print("💬 Для получения уведомлений используйте один из вариантов:")
        print("="*60)
        print(f"\n1️⃣  Ваш личный чат (Saved Messages) - РЕКОМЕНДУЕТСЯ:")
        print(f"   NOTIFY_CHAT_ID=me")
        print(f"   (Это самый простой способ - уведомления придут в 'Избранное')")
        
        print(f"\n2️⃣  Ваш user_id:")
        print(f"   NOTIFY_CHAT_ID={me.id}")
        
        print(f"\n3️⃣  Отправьте сообщение боту @userinfobot в Telegram")
        print(f"   Он покажет ваш chat_id")
        
        print(f"\n4️⃣  Создайте бота через @BotFather и отправьте ему /start")
        print(f"   Затем используйте его chat_id")
        
        print(f"\n5️⃣  Используйте другой канал/чат:")
        print(f"   - Откройте канал/чат в Telegram")
        print(f"   - Скопируйте ссылку (например: https://t.me/c/1234567890/1)")
        print(f"   - Число после /c/ - это chat_id (может быть отрицательным)")
        
        print("\n" + "="*60)
        print("📝 После получения chat_id добавьте его в .env файл:")
        print("   NOTIFY_CHAT_ID=ваш_chat_id")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()
        print("👋 Отключено от Telegram")

if __name__ == "__main__":
    try:
        asyncio.run(get_chat_id())
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")

