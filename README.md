# ContentAI Bot

Telegram-бот для генерации продающего контента для российского рынка.

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository_url>
cd contentai-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# или
source venv/bin/activate  # Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` из примера:
```bash
copy .env.example .env
```

5. Заполните переменные окружения в `.env`:
- `BOT_TOKEN` - токен бота от @BotFather
- `OPENROUTER_API_KEY` - ключ API OpenRouter (https://openrouter.ai/)

6. Запустите бота:
```bash
python main.py
```

## Команды

- `/start` - Начать работу
- `/help` - Помощь
- `/templates` - Выбрать шаблон
- `/settings` - Настройки
- `/history` - История генераций
- `/stats` - Статистика
- `/subscription` - Управление подпиской

## Технологии

- Python 3.11+
- aiogram 3.x
- OpenAI API
- SQLAlchemy 2.0
- aiosqlite