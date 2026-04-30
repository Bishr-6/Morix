# راوتر المعلم - Morix Platform
from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_user
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teacher", tags=["المعلم"])


def _require_teacher(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "manager", "admin", "owner"):
        raise HTTPException(status_code=403, detail="هذه الخدمة للمعلمين فقط")
    return current_user


# ============================================
# الواجبات
# ============================================
@router.get("/homework")
async def get_teacher_homework(current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    result = db.table("homework").select("*") \
        .eq("teacher_id", current_user["id"]) \
        .order("created_at", desc=True).execute()
    return result.data


@router.post("/homework")
async def create_homework(body: dict, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    title = body.get("title", "")
    description = body.get("description", "")
    subject = body.get("subject", current_user.get("subject", ""))
    grade = body.get("grade", "")
    topic = body.get("topic", "")

    # توليد بالذكاء الاصطناعي إذا طُلب أو إذا كان العنوان فارغاً مع وجود موضوع
    if body.get("ai_generate") or (topic and not title):
        from app.services.ai_service import chat_with_gemini
        msg = (
            f"Create a homework assignment for {subject} {'grade ' + grade if grade else ''} about: {topic or subject}.\n"
            f"Respond with ONLY:\nTITLE: [clear assignment title]\nINSTRUCTIONS: [detailed student instructions, 3-5 steps]"
        )
        reply, _ = await chat_with_gemini(message=msg, learning_style=None,
                                           full_name=current_user.get("full_name", "معلم"), role="teacher")
        lines = reply.strip().split("\n")
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("INSTRUCTIONS:"):
                description = line.replace("INSTRUCTIONS:", "").strip()
        if not title:
            title = f"واجب {subject} — {topic or ''}"
        if not description:
            description = reply

    result = db.table("homework").insert({
        "teacher_id": current_user["id"],
        "school_id": current_user.get("school_id"),
        "title": title or f"واجب {subject}",
        "description": description,
        "subject": subject,
        "grade": grade,
        "due_date": body.get("due_date"),
    }).execute()
    return result.data[0] if result.data else {"message": "تم إنشاء الواجب"}


@router.delete("/homework/{homework_id}")
async def delete_homework(homework_id: str, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    db.table("homework").delete().eq("id", homework_id).eq("teacher_id", current_user["id"]).execute()
    return {"message": "تم حذف الواجب"}


@router.get("/homework/{homework_id}/submissions")
async def get_submissions(homework_id: str, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    result = db.table("homework_submissions") \
        .select("*, users!student_id(full_name, grade)") \
        .eq("homework_id", homework_id).execute()
    return result.data


# ============================================
# الاختبارات
# ============================================
@router.get("/tests")
async def get_teacher_tests(current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    result = db.table("tests").select("id, title, subject, grade, duration_minutes, is_active, created_at") \
        .eq("teacher_id", current_user["id"]) \
        .order("created_at", desc=True).execute()
    return result.data


@router.post("/tests")
async def create_test(body: dict, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    questions = body.get("questions", [])

    # توليد بالذكاء الاصطناعي إذا طُلب
    if body.get("ai_generate") and body.get("subject"):
        from app.services.ai_service import generate_game_content
        content = await generate_game_content("mcq", body.get("subject", ""), body.get("topic", ""))
        if content and content.get("items"):
            questions = [
                {
                    "id": i + 1,
                    "question": item["question"],
                    "options": item["options"],
                    "answer": item["answer"],
                }
                for i, item in enumerate(content["items"])
            ]

    result = db.table("tests").insert({
        "teacher_id": current_user["id"],
        "school_id": current_user.get("school_id"),
        "title": body.get("title", "اختبار جديد"),
        "subject": body.get("subject", current_user.get("subject", "")),
        "grade": body.get("grade", ""),
        "questions": questions,
        "duration_minutes": body.get("duration_minutes", 60),
        "is_active": True,
    }).execute()
    return result.data[0] if result.data else {"message": "تم إنشاء الاختبار"}


@router.put("/tests/{test_id}")
async def update_test(test_id: str, body: dict, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    allowed = {k: body[k] for k in ("title", "questions", "duration_minutes", "is_active", "grade") if k in body}
    db.table("tests").update(allowed).eq("id", test_id).eq("teacher_id", current_user["id"]).execute()
    return {"message": "تم تحديث الاختبار"}


@router.delete("/tests/{test_id}")
async def delete_test(test_id: str, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    db.table("tests").delete().eq("id", test_id).eq("teacher_id", current_user["id"]).execute()
    return {"message": "تم حذف الاختبار"}


# ============================================
# أوراق العمل
# ============================================
@router.get("/worksheets")
async def get_teacher_worksheets(current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    result = db.table("worksheets").select("*") \
        .eq("teacher_id", current_user["id"]) \
        .order("created_at", desc=True).execute()
    return result.data


@router.post("/worksheets")
async def create_worksheet(body: dict, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    content = body.get("content", "")
    ai_generated = False

    if body.get("ai_generate"):
        from app.services.ai_service import chat_with_gemini
        subject = body.get("subject", "")
        topic = body.get("topic", "")
        msg = f"أنشئ ورقة عمل تعليمية شاملة عن مادة {subject}{f' - موضوع: {topic}' if topic else ''}. تضمين: الأهداف، الأنشطة، الأسئلة، والتقييم."
        reply, _ = await chat_with_gemini(
            message=msg,
            learning_style=None,
            full_name=current_user.get("full_name", "معلم"),
            role="teacher"
        )
        content = reply
        ai_generated = True

    result = db.table("worksheets").insert({
        "teacher_id": current_user["id"],
        "school_id": current_user.get("school_id"),
        "title": body.get("title", "ورقة عمل"),
        "subject": body.get("subject", current_user.get("subject", "")),
        "grade": body.get("grade", ""),
        "content": content,
        "ai_generated": ai_generated,
    }).execute()
    return result.data[0] if result.data else {"message": "تم إنشاء ورقة العمل", "content": content}


@router.delete("/worksheets/{worksheet_id}")
async def delete_worksheet(worksheet_id: str, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    db.table("worksheets").delete().eq("id", worksheet_id).eq("teacher_id", current_user["id"]).execute()
    return {"message": "تم حذف ورقة العمل"}


# ============================================
# الطلاب والتقدم
# ============================================
@router.get("/students")
async def get_students(current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    school_id = current_user.get("school_id")
    query = db.table("users").select(
        "id, full_name, grade, learning_style, stars_count, streak_count, created_at"
    ).eq("role", "student")
    if school_id:
        query = query.eq("school_id", school_id)
    result = query.order("full_name").execute()
    return result.data


@router.get("/students/{student_id}/progress")
async def get_student_progress(student_id: str, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    student = db.table("users").select("*").eq("id", student_id).execute()
    if not student.data:
        raise HTTPException(status_code=404, detail="الطالب غير موجود")

    streak = db.table("streaks").select("*").eq("user_id", student_id).execute()
    streak_data = streak.data[0] if streak.data else {}

    convs = db.table("ai_conversations").select("id", count="exact").eq("student_id", student_id).execute()
    test_res = db.table("test_results").select("score, completed_at").eq("student_id", student_id).execute()
    games = db.table("educational_games").select("score, completed, game_type") \
        .eq("student_id", student_id).eq("completed", True).execute()

    return {
        "student": {k: v for k, v in student.data[0].items() if k not in ("password_hash",)},
        "streak": streak_data,
        "total_conversations": len(convs.data or []),
        "test_results": test_res.data or [],
        "game_results": games.data or [],
    }


# ============================================
# توليد PPT وفيديو
# ============================================
@router.post("/generate-ppt")
async def generate_ppt(body: dict, current_user: dict = Depends(_require_teacher)):
    from app.services.ai_service import generate_ppt_outline

    title = body.get("title", "")
    subject = body.get("subject", "")
    content = body.get("content", "")

    if not title or not subject:
        raise HTTPException(status_code=400, detail="العنوان والمادة مطلوبان")

    result = await generate_ppt_outline(title, subject, content)
    if not result:
        raise HTTPException(status_code=500, detail="فشل توليد مخطط العرض")

    return {"outline": result}


@router.post("/generate-video")
async def generate_video_script(body: dict, current_user: dict = Depends(_require_teacher)):
    from app.services.ai_service import generate_video_script

    topic = body.get("topic", "")
    subject = body.get("subject", "")
    duration = body.get("duration_seconds", body.get("duration_minutes", 5) * 60)
    duration = max(30, min(600, int(duration)))

    if not topic:
        raise HTTPException(status_code=400, detail="الموضوع مطلوب")

    result = await generate_video_script(topic, subject, duration)
    if not result:
        raise HTTPException(status_code=500, detail="فشل توليد السكريبت")

    return {"script": result}


# ============================================
# الشات للمعلم
# ============================================
@router.post("/chat")
async def teacher_chat(body: dict, current_user: dict = Depends(_require_teacher)):
    from app.services.ai_service import chat_with_gemini

    message = body.get("message", "")
    image_base64 = body.get("image_base64")
    file_text = body.get("file_text")

    if not message and not image_base64 and not file_text:
        raise HTTPException(status_code=400, detail="الرسالة فارغة")

    reply, from_cache = await chat_with_gemini(
        message=message or "حلل هذا المحتوى للمعلم",
        learning_style=None,
        full_name=current_user.get("full_name", "معلم"),
        role="teacher",
        image_base64=image_base64,
        file_text=file_text,
    )
    return {"reply": reply, "from_cache": from_cache}


# ============================================
# الإعدادات
# ============================================
@router.get("/settings")
async def get_settings(current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    result = db.table("user_settings").select("*").eq("user_id", current_user["id"]).execute()
    settings = result.data[0] if result.data else {}
    return {
        "theme": settings.get("theme", "dark"),
        "brightness": settings.get("brightness", 100),
        "language": settings.get("language", "ar"),
        "notifications_enabled": settings.get("notifications_enabled", True),
        "avatar_url": current_user.get("avatar_url", ""),
        "email": current_user.get("email", ""),
        "full_name": current_user.get("full_name", ""),
    }


@router.put("/settings")
async def update_settings(body: dict, current_user: dict = Depends(_require_teacher), db=Depends(get_db)):
    existing = db.table("user_settings").select("id").eq("user_id", current_user["id"]).execute()
    data = {
        "user_id": current_user["id"],
        "theme": body.get("theme", "dark"),
        "brightness": body.get("brightness", 100),
        "language": body.get("language", "ar"),
        "notifications_enabled": body.get("notifications_enabled", True),
    }
    if existing.data:
        db.table("user_settings").update(data).eq("user_id", current_user["id"]).execute()
    else:
        db.table("user_settings").insert(data).execute()

    if body.get("avatar_url") is not None:
        db.table("users").update({"avatar_url": body["avatar_url"]}).eq("id", current_user["id"]).execute()

    return {"message": "تم حفظ الإعدادات"}
