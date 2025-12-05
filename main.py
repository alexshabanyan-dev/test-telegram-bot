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
# Используем абсолютный путь к .env файлу для работы с systemd
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Получаем данные из переменных окружения
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен бота для отправки уведомлений (опционально)
CHANNEL_NAME = os.getenv('CHANNEL_NAME', config.CHANNEL_NAME)
NOTIFY_CHAT_ID = os.getenv('NOTIFY_CHAT_ID')  # ID чата для уведомлений (ваш личный чат или другой канал)


def check_keywords(text: str) -> list:
    """
    Проверяет текст на наличие ключевых фраз
    Возвращает список найденных ключевых слов
    Все сравнения выполняются в нижнем регистре (case-insensitive)
    """
    if not text:
        return []
    
    found_keywords = []
    # Всегда переводим текст в нижний регистр для сравнения
    # Также нормализуем пробелы и убираем лишние символы
    text_to_check = text.lower().strip()
    
    # Сравниваем все ключевые слова в нижнем регистре
    for keyword in config.KEYWORDS:
        keyword_to_check = keyword.lower().strip()
        if keyword_to_check and keyword_to_check in text_to_check:
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
                               channel_name: str, message_id: int, channel_link: str = None, bot_client=None):
    """
    Отправляет уведомление в Telegram
    Использует бота, если указан BOT_TOKEN, иначе использует основной клиент
    """
    if not NOTIFY_CHAT_ID:
        return
    
    # Определяем какой клиент использовать для отправки
    send_client = bot_client if bot_client else client
    
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
            entity = 'me'
        else:
            try:
                chat_id = int(NOTIFY_CHAT_ID)
                # Пытаемся получить entity по ID
                try:
                    # Используем send_client для получения entity
                    entity = await send_client.get_entity(chat_id)
                except (ValueError, TypeError):
                    # Если не получается, пробуем разные форматы ID
                    # Для групп/каналов может быть -100XXXXXXXXXX или -XXXXXXXXXX
                    try:
                        # Если ID отрицательный и меньше 13 цифр, пробуем добавить -100
                        if chat_id < 0 and len(str(abs(chat_id))) < 13:
                            entity_with_prefix = int(f"-100{abs(chat_id)}")
                            entity = await send_client.get_entity(entity_with_prefix)
                        else:
                            # Пробуем отправить напрямую по числу
                            entity = chat_id
                    except:
                        # В последнюю очередь пробуем отправить напрямую
                        entity = chat_id
            except ValueError:
                # Если chat_id не число, используем как есть (username)
                entity = NOTIFY_CHAT_ID
        
        # Отправляем сообщение
        await send_client.send_message(entity, notification, parse_mode='markdown')
        sender = "бот" if bot_client else "аккаунт"
        print(f"✅ Уведомление отправлено в Telegram от {sender} (chat_id: {NOTIFY_CHAT_ID})")
        
    except ValueError as e:
        print(f"⚠️  Ошибка: Не удалось найти чат с ID {NOTIFY_CHAT_ID}")
        print(f"   Убедитесь, что:")
        print(f"   1. Бот добавлен в группу/канал")
        print(f"   2. Chat ID указан правильно")
        print(f"   3. Для групп используйте формат: -100XXXXXXXXXX или -XXXXXXXXXX")
    except Exception as e:
        print(f"⚠️  Ошибка при отправке уведомления в Telegram: {e}")


async def handler(event, channel_name: str, client: TelegramClient):
    """
    Обработчик новых сообщений из канала
    """
    message = event.message
    message_text = message.message or ""
    
    # Отладочное логирование (можно отключить позже)
    print(f"📨 Получено сообщение ID: {message.id}, Текст: {message_text[:100]}...")
    
    # Проверяем на наличие ключевых слов
    found_keywords = check_keywords(message_text)
    
    if found_keywords:
        print(f"✅ Найдены ключевые слова: {found_keywords}")
    else:
        # Отладочная информация для диагностики
        text_lower = message_text.lower() if message_text else ""
        print(f"ℹ️  Ключевые слова не найдены в сообщении")
        print(f"   Ищем: {[k.lower() for k in config.KEYWORDS]}")
        # Показываем весь текст (или первые 500 символов, если очень длинный)
        text_preview = text_lower if len(text_lower) <= 500 else text_lower[:500] + "..."
        print(f"   Текст целиком (в lower, {len(text_lower)} символов): {text_preview}")
        # Проверяем вручную для отладки
        for keyword in config.KEYWORDS:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower:
                # Находим позицию вхождения
                pos = text_lower.find(keyword_lower)
                context_start = max(0, pos - 20)
                context_end = min(len(text_lower), pos + len(keyword_lower) + 20)
                context = text_lower[context_start:context_end]
                print(f"   ⚠️  ОШИБКА: '{keyword_lower}' НАЙДЕНО в позиции {pos}!")
                print(f"      Контекст: ...{context}...")
    
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
        # Получаем bot_client из глобального контекста (если есть)
        bot_client = getattr(handler, 'bot_client', None)
        await notify_user_telegram(
            client=client,
            message_text=message_text,
            keywords=found_keywords,
            channel_name=channel_title,
            message_id=message.id,
            channel_link=channel_link,
            bot_client=bot_client
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
    
    # Инициализируем клиент для мониторинга (user account)
    # Используем абсолютный путь для файла сессии, чтобы избежать конфликтов
    import pathlib
    session_path = pathlib.Path('telegram_monitor.session').absolute()
    client = TelegramClient(str(session_path), API_ID, API_HASH)
    
    # Инициализируем бота для отправки уведомлений (если указан токен)
    bot_client = None
    if BOT_TOKEN:
        try:
            bot_session_path = pathlib.Path('telegram_bot.session').absolute()
            bot_client = TelegramClient(str(bot_session_path), API_ID, API_HASH)
            # Для бота используем токен вместо user account
            await bot_client.start(bot_token=BOT_TOKEN)
            print("✅ Бот подключен для отправки уведомлений")
            # Сохраняем bot_client в глобальном контексте для использования в handler
            handler.bot_client = bot_client
        except Exception as e:
            print(f"⚠️  Предупреждение: Не удалось подключить бота: {e}")
            print(f"   Уведомления будут отправляться от вашего аккаунта")
    
    # Подключаемся к Telegram с обработкой ошибок блокировки
    try:
        await client.start()
        print("✅ Подключение к Telegram установлено")
    except Exception as e:
        if "database is locked" in str(e).lower() or "locked" in str(e).lower():
            print("❌ Ошибка: Файл сессии заблокирован")
            print("   Возможно, другой процесс использует этот файл сессии")
            print("   Решение:")
            print("   1. Остановите все процессы бота: sudo systemctl stop telegram-monitor.service")
            print("   2. Удалите файлы блокировки: rm -f *.session-journal")
            print("   3. Запустите скрипт исправления: bash fix_session_lock.sh")
            return
        else:
            raise
    
    # Регистрируем обработчик событий ПОСЛЕ подключения
    # Используем entity вместо строки для более надежной работы
    try:
        channel_entity = await client.get_entity(CHANNEL_NAME)
        print(f"📡 Регистрирую обработчик для канала: {CHANNEL_NAME} (ID: {channel_entity.id})")
        
        @client.on(events.NewMessage(chats=channel_entity))
        async def message_handler(event):
            await handler(event, CHANNEL_NAME, client)
    except Exception as e:
        print(f"⚠️  Предупреждение: Не удалось получить entity канала, используем строку: {e}")
        @client.on(events.NewMessage(chats=CHANNEL_NAME))
        async def message_handler(event):
            await handler(event, CHANNEL_NAME, client)
    
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
        try:
            # Проверяем доступность чата для уведомлений
            await client.get_entity(int(NOTIFY_CHAT_ID))
            print(f"✅ Уведомления будут отправляться в чат: {NOTIFY_CHAT_ID}")
        except Exception as e:
            print(f"⚠️  Предупреждение: Не удалось проверить чат для уведомлений ({NOTIFY_CHAT_ID}): {e}")
            print(f"   Уведомления в Telegram могут не работать. Проверьте NOTIFY_CHAT_ID в .env")
    else:
        print("ℹ️  NOTIFY_CHAT_ID не указан - уведомления будут только в консоль")
        print("   Для получения уведомлений в Telegram укажите NOTIFY_CHAT_ID в .env")
    
    print("⏳ Ожидание новых сообщений... (Ctrl+C для остановки)\n")
    
    # Запускаем мониторинг
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Мониторинг остановлен пользователем")
    except Exception as e:
        error_msg = str(e).lower()
        if "database is locked" in error_msg or "locked" in error_msg:
            print(f"\n❌ Ошибка: Файл сессии заблокирован")
            print(f"   Выполните на сервере: bash fix_session_lock.sh")
        else:
            print(f"\n❌ Ошибка: {e}")

