from openai import AsyncOpenAI, APIError, RateLimitError, AuthenticationError
from bot.config import OPENROUTER_API_KEY
import logging

logger = logging.getLogger(__name__)

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY не установлен! Бот не сможет генерировать контент.")

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
) if OPENROUTER_API_KEY else None

async def generate_content(prompt: str, model: str = "meta-llama/llama-3.1-8b-instruct:free") -> str:
    if not client:
        return "Ошибка: API ключ OpenRouter не настроен. Обратитесь к администратору."
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты - эксперт по маркетингу и созданию контента для российского рынка. Пиши на русском языке, учитывая менталитет и особенности аудитории."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except AuthenticationError:
        logger.error("Ошибка аутентификации OpenRouter API")
        return "Ошибка: неверный API ключ. Обратитесь к администратору."
    except RateLimitError:
        logger.warning("Превышен лимит запросов OpenRouter API")
        return "Сервис временно перегружен. Попробуйте через минуту."
    except APIError as e:
        logger.error(f"Ошибка OpenRouter API: {e}")
        return "Произошла ошибка при генерации. Попробуйте позже."
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return "Произошла внутренняя ошибка. Попробуйте позже."