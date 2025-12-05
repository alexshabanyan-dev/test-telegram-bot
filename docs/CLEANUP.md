# Очистка проекта

## Файлы, которые можно удалить или оптимизировать:

### 1. Дублирующиеся скрипты:
- `check_running_bot.sh` - дублирует функциональность `check_bot_status.sh`
  - **Рекомендация:** Удалить `check_running_bot.sh`, оставить `check_bot_status.sh`

### 2. Тестовые файлы:
- `test_monitor.py` - тестовый скрипт для отладки
  - **Рекомендация:** Оставить (может быть полезен для диагностики)

### 3. Вспомогательные скрипты (можно организовать лучше):
Все эти скрипты полезны, но можно создать папку `scripts/`:
- `check_bot_status.sh`
- `debug_bot.sh`
- `fix_session_lock.sh`
- `force_restart_bot.sh`
- `setup_server.sh`
- `view_logs.sh`

## Файлы, которые правильно игнорируются (не в репозитории):
- `__pycache__/` ✅
- `telegram_monitor.session` ✅
- `venv/` ✅
- `.env` ✅

## Рекомендации:

1. **Удалить дублирующийся скрипт:**
   ```bash
   git rm check_running_bot.sh
   git commit -m "Remove duplicate check_running_bot.sh script"
   ```

2. **Опционально: создать папку scripts/** (для лучшей организации):
   ```bash
   mkdir scripts
   git mv *.sh scripts/
   git commit -m "Organize scripts into scripts/ directory"
   ```

