"""
Telegram Channel Monitor - MVP
Читает сообщения из открытого Telegram канала и ищет ключевые фразы
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import Channel
import config

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из переменных окружения
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
CHANNEL_NAME = os.getenv('CHANNEL_NAME', config.CHANNEL_NAME)


def check_keywords(text: str) -> list:
    """
    Проверяет текст на наличие ключевых фраз
    Возвращает список найденных ключевых слов
    """
    if not text:
        return []
    
    found_keywords = []
    text_to_check = text.lower() if config.CASE_INSENSITIVE else text
    
    for keyword in config.KEYWORDS:
        keyword_to_check = keyword.lower() if config.CASE_INSENSITIVE else keyword
        if keyword_to_check in text_to_check:
            found_keywords.append(keyword)
    
    return found_keywords


def notify_user(message_text: str, keywords: list, channel_name: str, message_id: int):
    """
    Уведомляет пользователя о найденном совпадении
    В MVP версии просто выводит в консоль
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*60)
    print(f"🔔 НАЙДЕНО СОВПАДЕНИЕ! [{timestamp}]")
    print(f"📺 Канал: {channel_name}")
    print(f"🔑 Ключевые слова: {', '.join(keywords)}")
    print(f"📝 Сообщение ID: {message_id}")
    print("-"*60)
    print(f"Текст сообщения:\n{message_text[:500]}...")  # Первые 500 символов
    print("="*60 + "\n")


async def handler(event, channel_name: str):
    """
    Обработчик новых сообщений из канала
    """
    message = event.message
    message_text = message.message or ""
    
    # Проверяем на наличие ключевых слов
    found_keywords = check_keywords(message_text)
    
    if found_keywords:
        # Получаем информацию о канале
        channel = await event.get_chat()
        channel_title = getattr(channel, 'title', channel_name) or channel_name
        
        # Уведомляем пользователя
        notify_user(
            message_text=message_text,
            keywords=found_keywords,
            channel_name=channel_title,
            message_id=message.id
        )


async def main():
    """
    Основная функция
    """
    print("🚀 Запуск Telegram Channel Monitor...")
    
    # Проверяем наличие необходимых данных
    if not API_ID or not API_HASH:
        print("❌ Ошибка: Не указаны API_ID и/или API_HASH в .env файле")
        return
    
    if not CHANNEL_NAME or CHANNEL_NAME == "your_channel_name_here":
        print("❌ Ошибка: Не указан CHANNEL_NAME в .env файле или config.py")
        return
    
    # Инициализируем клиент (внутри async функции)
    client = TelegramClient('telegram_monitor', API_ID, API_HASH)
    
    # Регистрируем обработчик событий
    @client.on(events.NewMessage(chats=CHANNEL_NAME))
    async def message_handler(event):
        await handler(event, CHANNEL_NAME)
    
    # Подключаемся к Telegram
    await client.start()
    print("✅ Подключение к Telegram установлено")
    
    # Получаем информацию о канале
    try:
        entity = await client.get_entity(CHANNEL_NAME)
        if isinstance(entity, Channel):
            print(f"📺 Мониторинг канала: {entity.title}")
            print(f"👁️  Подписчиков: {entity.participants_count if hasattr(entity, 'participants_count') else 'N/A'}")
        else:
            print(f"📺 Мониторинг: {CHANNEL_NAME}")
    except Exception as e:
        print(f"⚠️  Предупреждение: Не удалось получить информацию о канале: {e}")
        print(f"📺 Продолжаем мониторинг: {CHANNEL_NAME}")
    
    print(f"🔍 Ищем ключевые слова: {', '.join(config.KEYWORDS)}")
    print("⏳ Ожидание новых сообщений... (Ctrl+C для остановки)\n")
    
    # Запускаем мониторинг
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

