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
NOTIFY_CHAT_ID = os.getenv('NOTIFY_CHAT_ID')  # ID чата для уведомлений (ваш личный чат или другой канал)


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


def notify_user_console(message_text: str, keywords: list, channel_name: str, message_id: int):
    """
    Выводит уведомление в консоль
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


async def notify_user_telegram(client: TelegramClient, message_text: str, keywords: list, 
                               channel_name: str, message_id: int, channel_link: str = None):
    """
    Отправляет уведомление в Telegram
    """
    if not NOTIFY_CHAT_ID:
        return
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Формируем сообщение
        notification = f"🔔 **НАЙДЕНО СОВПАДЕНИЕ!**\n\n"
        notification += f"📺 **Канал:** {channel_name}\n"
        notification += f"🔑 **Ключевые слова:** {', '.join(keywords)}\n"
        notification += f"📝 **ID сообщения:** {message_id}\n"
        notification += f"🕐 **Время:** {timestamp}\n\n"
        
        if channel_link:
            notification += f"🔗 [Открыть канал]({channel_link})\n\n"
        
        notification += f"**Текст сообщения:**\n\n"
        notification += message_text[:2000]  # Ограничение длины сообщения в Telegram
        
        # Определяем куда отправлять
        if NOTIFY_CHAT_ID.lower() == 'me':
            # Отправляем в Saved Messages (Избранное)
            entity = 'me'
        else:
            # Преобразуем chat_id в число и пытаемся получить entity
            try:
                chat_id = int(NOTIFY_CHAT_ID)
                # Пытаемся получить entity по ID
                try:
                    entity = await client.get_entity(chat_id)
                except ValueError:
                    # Если не получается по ID, пробуем отправить напрямую по числу
                    entity = chat_id
            except ValueError:
                # Если chat_id не число, используем как есть (username)
                entity = NOTIFY_CHAT_ID
        
        # Отправляем сообщение
        await client.send_message(entity, notification, parse_mode='markdown')
        print(f"✅ Уведомление отправлено в Telegram (chat_id: {NOTIFY_CHAT_ID})")
        
    except ValueError as e:
        print(f"⚠️  Ошибка: Не удалось найти чат с ID {NOTIFY_CHAT_ID}")
        print(f"   Убедитесь, что:")
        print(f"   1. Вы отправили хотя бы одно сообщение боту/в чат")
        print(f"   2. Chat ID указан правильно")
        print(f"   3. Для личных сообщений используйте 'me' вместо chat_id")
    except Exception as e:
        print(f"⚠️  Ошибка при отправке уведомления в Telegram: {e}")


async def handler(event, channel_name: str, client: TelegramClient):
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
        
        # Формируем ссылку на канал
        channel_link = None
        if hasattr(channel, 'username') and channel.username:
            channel_link = f"https://t.me/{channel.username}/{message.id}"
        
        # Выводим в консоль
        notify_user_console(
            message_text=message_text,
            keywords=found_keywords,
            channel_name=channel_title,
            message_id=message.id
        )
        
        # Отправляем в Telegram
        await notify_user_telegram(
            client=client,
            message_text=message_text,
            keywords=found_keywords,
            channel_name=channel_title,
            message_id=message.id,
            channel_link=channel_link
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
        await handler(event, CHANNEL_NAME, client)
    
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
    
    # Проверяем настройку уведомлений
    if NOTIFY_CHAT_ID:
        if NOTIFY_CHAT_ID.lower() == 'me':
            print(f"✅ Уведомления будут отправляться в Saved Messages (Избранное)")
        else:
            try:
                # Пытаемся преобразовать в число
                chat_id = int(NOTIFY_CHAT_ID)
                try:
                    # Пытаемся получить entity
                    entity = await client.get_entity(chat_id)
                    print(f"✅ Уведомления будут отправляться в чат: {NOTIFY_CHAT_ID}")
                except ValueError:
                    print(f"⚠️  Предупреждение: Не удалось найти чат с ID {NOTIFY_CHAT_ID}")
                    print(f"   Попробуйте:")
                    print(f"   1. Использовать 'me' для отправки в Saved Messages")
                    print(f"   2. Отправить сообщение боту/в чат перед запуском")
                    print(f"   3. Проверить правильность chat_id")
            except ValueError:
                # Если не число, возможно это username
                try:
                    entity = await client.get_entity(NOTIFY_CHAT_ID)
                    print(f"✅ Уведомления будут отправляться в: {NOTIFY_CHAT_ID}")
                except Exception as e:
                    print(f"⚠️  Предупреждение: Не удалось проверить чат ({NOTIFY_CHAT_ID}): {e}")
    else:
        print("ℹ️  NOTIFY_CHAT_ID не указан - уведомления будут только в консоль")
        print("   Для получения уведомлений в Telegram укажите NOTIFY_CHAT_ID в .env")
        print("   Используйте 'me' для отправки в Saved Messages")
    
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

