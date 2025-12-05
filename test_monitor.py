"""
Тестовый скрипт для проверки работы мониторинга
Показывает все сообщения из канала для отладки
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import Channel

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из переменных окружения
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
CHANNEL_NAME = os.getenv('CHANNEL_NAME', '@test_sae')

async def test_monitor():
    """
    Тестовый мониторинг - показывает все сообщения
    """
    if not API_ID or not API_HASH:
        print("❌ Ошибка: Не указаны API_ID и/или API_HASH в .env файле")
        return
    
    # Инициализируем клиент
    client = TelegramClient('telegram_monitor', API_ID, API_HASH)
    
    # Регистрируем обработчик для всех сообщений
    @client.on(events.NewMessage(chats=CHANNEL_NAME))
    async def message_handler(event):
        message = event.message
        message_text = message.message or ""
        
        print("\n" + "="*60)
        print(f"📨 НОВОЕ СООБЩЕНИЕ!")
        print(f"📝 ID: {message.id}")
        print(f"📅 Дата: {message.date}")
        print(f"👤 От: {message.from_id}")
        print(f"💬 Текст: {message_text}")
        print("="*60 + "\n")
    
    try:
        # Подключаемся к Telegram
        await client.start()
        print("✅ Подключение к Telegram установлено")
        
        # Получаем информацию о канале
        try:
            entity = await client.get_entity(CHANNEL_NAME)
            if isinstance(entity, Channel):
                print(f"📺 Мониторинг канала: {entity.title}")
                print(f"🆔 ID канала: {entity.id}")
                if entity.username:
                    print(f"🌐 Username: @{entity.username}")
            else:
                print(f"📺 Мониторинг: {CHANNEL_NAME}")
        except Exception as e:
            print(f"⚠️  Предупреждение: {e}")
        
        print(f"👀 Ожидание сообщений из канала {CHANNEL_NAME}...")
        print("   Отправьте тестовое сообщение в канал\n")
        
        # Запускаем мониторинг
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(test_monitor())
    except KeyboardInterrupt:
        print("\n\n👋 Тест прерван пользователем")

