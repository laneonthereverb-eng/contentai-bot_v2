from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, date

from bot.database import User, GenerationHistory, UserRole, get_session
from bot.templates import TEMPLATES, TONES, LANGUAGES
from bot.utils.openai_client import generate_content
from bot.config import FREE_TIER_LIMIT

router = Router()

class GenerationState(StatesGroup):
    waiting_for_topic = State()
    waiting_for_tone = State()
    waiting_for_template = State()

@router.message(F.text == "vk_post")
@router.message(F.text == "product_description")
@router.message(F.text == "ad_text")
@router.message(F.text == "headline")
@router.message(F.text == "telegram_channel")
async def select_template(message: Message, state: FSMContext):
    template_key = message.text
    if template_key not in TEMPLATES:
        await message.answer("Шаблон не найден. Используйте /templates")
        return
    
    await state.update_data(template_key=template_key)
    await state.set_state(GenerationState.waiting_for_topic)
    
    template = TEMPLATES[template_key]
    await message.answer(
        f"Вы выбрали: {template['name']}\n\n"
        f"Описание: {template['description']}\n\n"
        "Теперь напишите тему для контента:"
    )

@router.message(GenerationState.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3 or len(topic) > 500:
        await message.answer("Тема должна быть от 3 до 500 символов. Попробуйте ещё раз:")
        return
    await state.update_data(topic=topic)
    await state.set_state(GenerationState.waiting_for_tone)
    
    tones_text = "Выберите тон общения:\n\n"
    for key, tone in TONES.items():
        tones_text += f"• {key} - {tone}\n"
    
    await message.answer(tones_text)

@router.message(GenerationState.waiting_for_tone)
async def process_tone(message: Message, state: FSMContext):
    tone = message.text.lower()
    if tone not in TONES:
        await message.answer("Тон не распознан. Выберите: formal, informal, friendly, expert")
        return
    
    await state.update_data(tone=tone)
    
    data = await state.get_data()
    template_key = data["template_key"]
    topic = data["topic"]
    
    template = TEMPLATES[template_key]
    prompt = template["prompt_template"].format(
        topic=topic,
        tone=TONES[tone],
        audience="малый бизнес и начинающие SMM-специалисты"
    )
    
    await message.answer("⏳ Генерирую контент...")
    
    result = await generate_content(prompt)
    
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Сначала выполните /start")
            await state.clear()
            return
        
        today = date.today()
        if user.last_generation_date and user.last_generation_date.date() != today:
            user.generations_today = 0
        
        if user.role == UserRole.FREE and user.generations_today >= FREE_TIER_LIMIT:
            await message.answer(
                "❌ Лимит генераций на сегодня исчерпан!\n\n"
                "Обновите подписку: /subscription"
            )
            await state.clear()
            return
        
        history = GenerationHistory(
            user_id=message.from_user.id,
            template_name=template["name"],
            prompt=prompt,
            result=result,
            created_at=datetime.utcnow()
        )
        session.add(history)
        
        user.generations_today += 1
        user.last_generation_date = datetime.utcnow()
        
        await session.commit()
    
    await message.answer(result)
    await state.clear()

@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery):
    try:
        history_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("Ошибка: неверный формат данных")
        return
    
    if history_id <= 0:
        await callback.answer("Ошибка: неверный ID")
        return
    
    async with get_session() as session:
        from bot.database import GenerationHistory
        from sqlalchemy import select, update
        stmt = select(GenerationHistory).where(GenerationHistory.id == history_id)
        result = await session.execute(stmt)
        history_item = result.scalar_one_or_none()
        
        if history_item:
            await session.execute(
                update(GenerationHistory)
                .where(GenerationHistory.id == history_id)
                .values(is_liked=True)
            )
            await session.commit()
            await callback.answer("Спасибо за оценку! 👍")
        else:
            await callback.answer("Не удалось обработать оценку")