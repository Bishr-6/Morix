# راوتر الذكاء الاصطناعي - Morix Platform
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ChatMessage, ChatResponse, ImageGenerateRequest
from app.services.ai_service import chat_with_gemini, generate_educational_image
from app.auth import get_current_user
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["الذكاء الاصطناعي"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """الشات مع الذكاء الاصطناعي - يدعم الطالب والمعلم والمالك"""
    role = current_user["role"]

    conversation_id = message.conversation_id
    if not conversation_id:
        conv_data = {
            "student_id": current_user["id"],
            "title": message.message[:50] + ("..." if len(message.message) > 50 else ""),
        }
        if message.book_id:
            conv_data["book_id"] = message.book_id

        conv = db.table("ai_conversations").insert(conv_data).execute()
        conversation_id = conv.data[0]["id"]
    elif message.book_id:
        db.table("ai_conversations").update({"book_id": message.book_id}) \
            .eq("id", conversation_id).execute()

    history = db.table("ai_messages") \
        .select("role, content") \
        .eq("conversation_id", conversation_id) \
        .order("created_at") \
        .execute()

    book_summary = None
    if message.book_id:
        book = db.table("curriculum_books").select("summary, title").eq("id", message.book_id).execute()
        if book.data and book.data[0].get("summary"):
            book_summary = f"Book: {book.data[0]['title']}\n{book.data[0]['summary']}"

    # جلب إعدادات المستخدم (صعوبة اللغة)
    difficulty = "medium"
    try:
        s = db.table("user_settings").select("difficulty").eq("user_id", current_user["id"]).execute()
        if s.data:
            difficulty = s.data[0].get("difficulty", "medium")
    except Exception:
        pass

    learning_style = current_user.get("learning_style") if role == "student" else None
    full_name = current_user.get("full_name", "مستخدم")

    reply, from_cache = await chat_with_gemini(
        message=message.message,
        learning_style=learning_style,
        book_summary=book_summary,
        conversation_history=history.data if history.data else [],
        full_name=full_name,
        role=role,
        difficulty=difficulty,
        image_base64=message.image_base64,
        file_text=message.file_text,
    )

    db.table("ai_messages").insert({"conversation_id": conversation_id, "role": "user", "content": message.message}).execute()
    db.table("ai_messages").insert({"conversation_id": conversation_id, "role": "assistant", "content": reply}).execute()

    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "ai_chat",
            "event_data": {"from_cache": from_cache, "role": role}
        }).execute()
    except Exception:
        pass

    return ChatResponse(conversation_id=conversation_id, reply=reply, from_cache=from_cache)


@router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = db.table("ai_conversations") \
        .select("id, title, created_at, book_id, curriculum_books(title)") \
        .eq("student_id", current_user["id"]) \
        .order("created_at", desc=True).execute()
    return result.data


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    conv = db.table("ai_conversations") \
        .select("*").eq("id", conversation_id).eq("student_id", current_user["id"]).execute()
    if not conv.data:
        raise HTTPException(status_code=404, detail="المحادثة غير موجودة")

    messages = db.table("ai_messages") \
        .select("*").eq("conversation_id", conversation_id).order("created_at").execute()
    return {"conversation": conv.data[0], "messages": messages.data}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    conv = db.table("ai_conversations") \
        .select("id").eq("id", conversation_id).eq("student_id", current_user["id"]).execute()
    if not conv.data:
        raise HTTPException(status_code=404, detail="المحادثة غير موجودة")
    db.table("ai_conversations").delete().eq("id", conversation_id).execute()
    return {"message": "تم حذف المحادثة"}


@router.get("/books")
async def get_books_for_chat(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = db.table("curriculum_books").select("id, title, subject, grade, summary").eq("is_active", True).execute()
    return result.data


@router.post("/generate-image")
async def generate_image(request: ImageGenerateRequest, current_user: dict = Depends(get_current_user)):
    """توليد صورة تعليمية بالذكاء الاصطناعي"""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="الوصف فارغ")

    result = await generate_educational_image(request.prompt)

    if not result.get("success"):
        return {
            "success": False,
            "message": result.get("error") or "تعذر توليد الصورة",
            "image": None,
            "details": result.get("details", ""),
        }
    image_b64 = result["image"]

    return {"success": True, "image": image_b64, "prompt": request.prompt}
