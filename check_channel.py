"""
Скрипт для проверки доступности Telegram канала
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Channel
import sys

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из переменных окружения
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

async def check_channel(channel_name: str):
    """
    Проверяет доступность канала
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
        
        # Пробуем получить информацию о канале
        print(f"🔍 Проверяю канал: {channel_name}")
        try:
            entity = await client.get_entity(channel_name)
            
            if isinstance(entity, Channel):
                print(f"\n✅ Канал найден!")
                print(f"📺 Название: {entity.title}")
                print(f"👁️  Подписчиков: {entity.participants_count if hasattr(entity, 'participants_count') else 'N/A'}")
                print(f"🆔 ID канала: {entity.id}")
                
                # Проверяем, является ли канал публичным
                if entity.username:
                    print(f"🌐 Username: @{entity.username}")
                    print(f"✅ Канал ПУБЛИЧНЫЙ (есть username)")
                    print(f"🔗 Ссылка: https://t.me/{entity.username}")
                else:
                    print(f"🔒 Канал ПРИВАТНЫЙ (нет username)")
                
                # Проверяем доступ
                if entity.access_hash:
                    print(f"✅ Доступ к каналу есть (access_hash присутствует)")
                else:
                    print(f"⚠️  Доступ к каналу может быть ограничен")
                    
            else:
                print(f"⚠️  Найдена сущность, но это не канал (тип: {type(entity).__name__})")
                
        except ValueError as e:
            print(f"❌ Канал не найден или недоступен")
            print(f"   Ошибка: {e}")
            print(f"\n💡 Возможные причины:")
            print(f"   - Канал приватный и вы не подписаны")
            print(f"   - Неправильное имя канала")
            print(f"   - Канал удален или не существует")
            
    except Exception as e:
        print(f"❌ Ошибка при подключении: {e}")
    finally:
        await client.disconnect()
        print("\n👋 Отключено от Telegram")

if __name__ == "__main__":
    # Получаем имя канала из аргументов или используем дефолтное
    channel_name = sys.argv[1] if len(sys.argv) > 1 else "@vmestesilamoscow"
    
    # Убираем @ если есть
    if channel_name.startswith('@'):
        channel_name = channel_name[1:]
    channel_name = f"@{channel_name}"
    
    try:
        asyncio.run(check_channel(channel_name))
    except KeyboardInterrupt:
        print("\n\n👋 Проверка прервана пользователем")

