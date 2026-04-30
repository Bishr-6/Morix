# خدمة تلخيص الكتب - Gemini
import logging
from typing import Optional
from app.config import settings
from app.services.cache_service import get_cached, set_cached, make_cache_key, SUMMARY_TTL_HOURS

logger = logging.getLogger(__name__)


async def summarize_book(title: str, subject: str, raw_text: str) -> Optional[str]:
    """توليد ملخص كتاب مدرسي باستخدام Gemini"""

    cache_key = make_cache_key("book_summary", title, subject, raw_text[:200])
    cached = await get_cached(cache_key)
    if cached:
        return cached.get("summary")

    if not settings.gemini_api_key or settings.gemini_api_key == "YOUR_GEMINI_API_KEY":
        return f"[ملخص تجريبي] كتاب {title} - مادة {subject}."

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        prompt = (
            f"أنت خبير تربوي. لخص محتوى هذا الكتاب المدرسي بشكل مفيد للطلاب.\n\n"
            f"عنوان الكتاب: {title}\nالمادة: {subject}\n\nالنص:\n{raw_text[:5000]}\n\n"
            f"اكتب ملخصاً شاملاً يتضمن الموضوعات الرئيسية والمفاهيم الأساسية والأهداف التعليمية. "
            f"باللغة العربية ولا يتجاوز 500 كلمة."
        )

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )
        summary = response.text
        await set_cached(cache_key, "book_summary", {"summary": summary}, SUMMARY_TTL_HOURS)
        return summary

    except Exception as e:
        logger.error(f"Book summarizer error: {e}")
        return None
