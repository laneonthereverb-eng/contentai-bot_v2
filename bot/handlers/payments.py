from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bot.database import User, UserRole, get_session
from bot.config import START_TIER_PRICE, BUSINESS_TIER_PRICE, AGENCY_TIER_PRICE

router = Router()

PRICES = {
    "start": START_TIER_PRICE,
    "business": BUSINESS_TIER_PRICE,
    "agency": AGENCY_TIER_PRICE
}

@router.message(F.text.startswith("купить "))
async def process_purchase(message: Message):
    tier = message.text.replace("купить ", "").strip().lower()
    
    if tier not in PRICES:
        await message.answer(
            "❌ Тариф не найден.\n\n"
            "Доступные тарифы:\n"
            "• start - 299 ₽\n"
            "• business - 599 ₽\n"
            "• agency - 1499 ₽"
        )
        return
    
    price = PRICES[tier]
    
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Сначала выполните /start")
            return
    
    payment_text = f"""
💳 Оплата тарифа: {tier.title()}

Сумма: {price} ₽/мес

Для оплаты нажмите кнопку ниже:
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"Оплатить {price} ₽",
            callback_data=f"pay_{tier}"
        )]
    ])
    
    await message.answer(payment_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery):
    tier = callback.data.replace("pay_", "").strip().lower()
    if not tier or len(tier) > 20:
        await callback.answer("Ошибка: неверный формат данных")
        return
    
    if tier not in PRICES:
        await callback.answer("Ошибка: тариф не найден")
        return
    
    async with get_session() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            await callback.answer("Ошибка: пользователь не найден")
            return
        
        role_map = {
            "start": UserRole.START,
            "business": UserRole.BUSINESS,
            "agency": UserRole.AGENCY
        }
        
        user.role = role_map[tier]
        await session.commit()
    
    await callback.message.edit_text(
        f"✅ Оплата прошла успешно!\n\n"
        f"Ваш тариф обновлен до: {tier.title()}\n\n"
        "Теперь вам доступны все функции тарифа!"
    )
    await callback.answer()