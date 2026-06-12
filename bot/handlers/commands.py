from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, date

from bot.database import User, UserRole, get_session
from bot.config import FREE_TIER_LIMIT

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                role=UserRole.FREE,
                generations_today=0,
                last_generation_date=datetime.utcnow()
            )
            session.add(user)
            await session.commit()

    welcome_text = f"""
Привет, {message.from_user.first_name}! 👋

Я - ContentAI Bot, ваш персональный помощник для создания продающего контента.

🎯 Что я умею:
• Писать посты для ВКонтакте
• Создавать описания товаров
• Генерировать рекламные тексты
• Придумывать заголовки
• Создавать контент для Telegram

📌 Бесплатно: {FREE_TIER_LIMIT} генерации в день

Начните с команды /templates чтобы выбрать шаблон!
"""
    await message.answer(welcome_text)

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📖 Команды бота:

/start - Начать работу
/help - Помощь
/templates - Выбрать шаблон контента
/settings - Настройки (тон, язык)
/history - История генераций
/stats - Ваша статистика
/subscription - Управление подпиской

💡 Просто напишите тему после выбора шаблона, и я создам контент!
"""
    await message.answer(help_text)

@router.message(Command("templates"))
async def cmd_templates(message: Message):
    from bot.templates import TEMPLATES
    
    text = "📝 Доступные шаблоны:\n\n"
    for key, template in TEMPLATES.items():
        text += f"🔹 {template['name']}\n{template['description']}\n\n"
    
    text += "Выберите шаблон, написав его название или номер."
    await message.answer(text)

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    settings_text = """
⚙️ Настройки:

1️⃣ Тон общения:
• formal - Формальный
• informal - Неформальный
• friendly - Дружеский
• expert - Экспертный

2️⃣ Язык:
• ru - Русский
• en - Английский

Напишите "тон [название]" или "язык [название]" для изменения.
"""
    await message.answer(settings_text)

@router.message(Command("history"))
async def cmd_history(message: Message):
    async with get_session() as session:
        from bot.database import GenerationHistory
        from sqlalchemy import select
        stmt = select(GenerationHistory).where(
            GenerationHistory.user_id == message.from_user.id
        ).order_by(GenerationHistory.created_at.desc()).limit(10)
        result = await session.execute(stmt)
        history = result.scalars().all()
    
    if not history:
        await message.answer("📭 История пуста. Начните генерировать контент!")
        return
    
    text = "📜 Последние 10 генераций:\n\n"
    for i, item in enumerate(history, 1):
        text += f"{i}. {item.template_name} - {item.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    
    await message.answer(text)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Сначала выполните /start")
            return
        
        from bot.database import GenerationHistory
        from sqlalchemy import select, func
        stmt = select(func.count(GenerationHistory.id)).where(
            GenerationHistory.user_id == message.from_user.id
        )
        result = await session.execute(stmt)
        total_count = result.scalar()
        
        today_count = user.generations_today
        total_count = len(all_generations)
        
        stats_text = f"""
📊 Ваша статистика:

• Роль: {user.role.value}
• Генераций сегодня: {today_count}/{FREE_TIER_LIMIT if user.role == UserRole.FREE else '∞'}
• Всего генераций: {total_count}
• Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}
"""
        await message.answer(stats_text)

@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Сначала выполните /start")
            return
    
    sub_text = f"""
💳 Текущая подписка: {user.role.value}

📦 Доступные тарифы:

🆓 Free - 0 ₽
• 3 генерации/день
• Базовые шаблоны

🚀 Старт - 299 ₽/мес
• 30 генераций/день
• Все шаблоны
• История генераций

💼 Бизнес - 599 ₽/мес
• Безлимит
• Все функции
• Экспорт в PDF

🏢 Агентство - 1499 ₽/мес
• 5 пользователей
• White-label
• API доступ

Для оплаты напишите "купить [тариф]"
"""
    await message.answer(sub_text)