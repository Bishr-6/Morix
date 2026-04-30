# راوتر الطالب - Morix Platform
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import DiagnosticSubmit, DiagnosticResult, ComplaintCreate, UserSettingsUpdate
from app.auth import get_current_user
from app.database import get_db
import logging
from datetime import date, datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/student", tags=["الطالب"])

DIAGNOSTIC_QUESTIONS = [
    {
        "id": 1,
        "question": "عندما تتعلم شيئاً جديداً، تفضل:",
        "options": [
            {"value": "visual", "text": "مشاهدة صور ورسوم توضيحية"},
            {"value": "auditory", "text": "الاستماع لشرح تفصيلي"},
            {"value": "kinesthetic", "text": "التجربة والممارسة العملية"},
        ]
    },
    {
        "id": 2,
        "question": "في الفصل الدراسي، تستفيد أكثر من:",
        "options": [
            {"value": "visual", "text": "الكتابة على السبورة والمخططات"},
            {"value": "auditory", "text": "شرح المعلم والنقاش"},
            {"value": "kinesthetic", "text": "الأنشطة والتجارب"},
        ]
    },
    {
        "id": 3,
        "question": "عند حل مشكلة صعبة، تميل إلى:",
        "options": [
            {"value": "visual", "text": "رسم مخطط أو خريطة ذهنية"},
            {"value": "auditory", "text": "مناقشتها مع شخص آخر"},
            {"value": "kinesthetic", "text": "تجربة حلول مختلفة بالتسلسل"},
        ]
    },
    {
        "id": 4,
        "question": "لتتذكر المعلومات بشكل أفضل:",
        "options": [
            {"value": "visual", "text": "تصنع جداول وقوائم ملونة"},
            {"value": "auditory", "text": "تكرر المعلومات بصوت عالٍ"},
            {"value": "kinesthetic", "text": "تكتب الملخصات بخط يدك"},
        ]
    },
    {
        "id": 5,
        "question": "وقت الفراغ، تفضل:",
        "options": [
            {"value": "visual", "text": "مشاهدة أفلام أو صور"},
            {"value": "auditory", "text": "الاستماع للموسيقى أو البودكاست"},
            {"value": "kinesthetic", "text": "ممارسة رياضة أو نشاط حركي"},
        ]
    },
]

STYLE_DESCRIPTIONS = {
    "visual": "أنت متعلم بصري! تفضل المعلومات المرئية كالرسوم والمخططات والألوان.",
    "auditory": "أنت متعلم سمعي! تفضل الشرح الشفهي والنقاش والاستماع.",
    "kinesthetic": "أنت متعلم حركي! تفضل التعلم بالتجربة والممارسة العملية.",
}


def _require_student(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("student", "owner"):
        raise HTTPException(status_code=403, detail="هذه الخدمة للطلاب فقط")
    return current_user


@router.get("/diagnostic/questions")
async def get_diagnostic_questions(current_user: dict = Depends(_require_student)):
    return DIAGNOSTIC_QUESTIONS


@router.post("/diagnostic/submit", response_model=DiagnosticResult)
async def submit_diagnostic(
    submission: DiagnosticSubmit,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db)
):
    scores = {"visual": 0, "auditory": 0, "kinesthetic": 0}
    for answer in submission.answers:
        if answer.answer in scores:
            scores[answer.answer] += 1

    dominant_style = max(scores, key=scores.get)

    db.table("users").update({"learning_style": dominant_style}).eq("id", current_user["id"]).execute()

    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "diagnostic_completed",
            "event_data": {"learning_style": dominant_style, "scores": scores}
        }).execute()
    except Exception:
        pass

    return DiagnosticResult(
        learning_style=dominant_style,
        visual_score=scores["visual"],
        auditory_score=scores["auditory"],
        kinesthetic_score=scores["kinesthetic"],
        description=STYLE_DESCRIPTIONS[dominant_style]
    )


@router.get("/profile")
async def get_student_profile(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    streak = db.table("streaks").select("*").eq("user_id", current_user["id"]).execute()
    streak_data = streak.data[0] if streak.data else {"current_streak": 0, "total_stars": 0, "longest_streak": 0}
    return {
        "id": current_user["id"],
        "name": current_user["full_name"],
        "email": current_user["email"],
        "grade": current_user.get("grade"),
        "learning_style": current_user.get("learning_style"),
        "must_change_password": current_user.get("must_change_password", False),
        "avatar_url": current_user.get("avatar_url"),
        "stars_count": streak_data.get("total_stars", 0),
        "streak_count": streak_data.get("current_streak", 0),
        "longest_streak": streak_data.get("longest_streak", 0),
    }


# ============================================
# الإعدادات
# ============================================
@router.get("/settings")
async def get_settings(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = db.table("user_settings").select("*").eq("user_id", current_user["id"]).execute()
    base = {"theme": "dark", "notifications_enabled": True, "brightness": 100,
            "difficulty": "medium", "hobbies": [], "language": "ar",
            "avatar_url": current_user.get("avatar_url", "")}
    if not result.data:
        return base
    s = result.data[0]
    data = {k: v for k, v in s.items() if k not in ("id", "user_id", "created_at", "updated_at")}
    data["avatar_url"] = current_user.get("avatar_url", "")
    return data


@router.put("/settings")
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    all_data = settings_data.model_dump(exclude_none=True)

    # avatar_url يُخزَّن في جدول users وليس user_settings
    avatar_url = all_data.pop("avatar_url", None)
    if avatar_url is not None:
        db.table("users").update({"avatar_url": avatar_url}).eq("id", current_user["id"]).execute()

    if all_data:
        all_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        existing = db.table("user_settings").select("id").eq("user_id", current_user["id"]).execute()
        if existing.data:
            db.table("user_settings").update(all_data).eq("user_id", current_user["id"]).execute()
        else:
            all_data["user_id"] = current_user["id"]
            db.table("user_settings").insert(all_data).execute()

    return {"message": "تم حفظ الإعدادات"}


# ============================================
# الواجبات
# ============================================
@router.get("/homework")
async def get_homework(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    school_id = current_user.get("school_id")
    grade = current_user.get("grade")

    query = db.table("homework").select("*, users!teacher_id(full_name)")
    if school_id:
        query = query.eq("school_id", school_id)
    if grade:
        query = query.eq("grade", grade)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.post("/homework/{homework_id}/submit")
async def submit_homework(
    homework_id: str,
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db)
):
    existing = db.table("homework_submissions") \
        .select("id").eq("homework_id", homework_id).eq("student_id", current_user["id"]).execute()
    if existing.data:
        db.table("homework_submissions").update({"content": body.get("content", "")}) \
            .eq("homework_id", homework_id).eq("student_id", current_user["id"]).execute()
    else:
        db.table("homework_submissions").insert({
            "homework_id": homework_id,
            "student_id": current_user["id"],
            "content": body.get("content", "")
        }).execute()
    return {"message": "تم تسليم الواجب"}


# ============================================
# الاختبارات
# ============================================
@router.get("/tests")
async def get_tests(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    school_id = current_user.get("school_id")
    grade = current_user.get("grade")

    query = db.table("tests").select("id, title, subject, grade, duration_minutes, created_at").eq("is_active", True)
    if school_id:
        query = query.eq("school_id", school_id)
    if grade:
        query = query.eq("grade", grade)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/tests/{test_id}")
async def get_test(test_id: str, current_user: dict = Depends(_require_student), db=Depends(get_db)):
    result = db.table("tests").select("*").eq("id", test_id).eq("is_active", True).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="الاختبار غير موجود")
    return result.data[0]


@router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: str,
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db)
):
    # حساب الدرجة
    test = db.table("tests").select("questions").eq("id", test_id).execute()
    if not test.data:
        raise HTTPException(status_code=404, detail="الاختبار غير موجود")

    questions = test.data[0].get("questions", [])
    answers = body.get("answers", {})

    correct = 0
    for q in questions:
        qid = str(q.get("id", ""))
        if answers.get(qid) == q.get("answer"):
            correct += 1

    score = (correct / len(questions) * 100) if questions else 0

    db.table("test_results").insert({
        "test_id": test_id,
        "student_id": current_user["id"],
        "answers": answers,
        "score": round(score, 1)
    }).execute()

    return {"score": round(score, 1), "correct": correct, "total": len(questions)}


# ============================================
# أوراق العمل
# ============================================
@router.get("/worksheets")
async def get_worksheets(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    school_id = current_user.get("school_id")
    grade = current_user.get("grade")

    query = db.table("worksheets").select("id, title, subject, grade, ai_generated, created_at")
    if school_id:
        query = query.eq("school_id", school_id)
    if grade:
        query = query.eq("grade", grade)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/worksheets/{worksheet_id}")
async def get_worksheet(worksheet_id: str, current_user: dict = Depends(_require_student), db=Depends(get_db)):
    result = db.table("worksheets").select("*").eq("id", worksheet_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="ورقة العمل غير موجودة")
    return result.data[0]


# ============================================
# الألعاب التعليمية
# ============================================
@router.get("/games")
async def get_games(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    result = db.table("educational_games").select("*") \
        .eq("student_id", current_user["id"]) \
        .order("created_at", desc=True).limit(20).execute()
    return result.data


@router.post("/games")
async def create_game(body: dict, current_user: dict = Depends(_require_student), db=Depends(get_db)):
    from app.services.ai_service import generate_game_content

    game_type = body.get("game_type", "mcq")
    subject = body.get("subject", "")
    topic = body.get("topic", "")

    content = await generate_game_content(game_type, subject, topic)
    if not content:
        raise HTTPException(status_code=500, detail="فشل توليد اللعبة")

    result = db.table("educational_games").insert({
        "student_id": current_user["id"],
        "game_type": game_type,
        "subject": subject,
        "content": content,
    }).execute()

    return result.data[0] if result.data else content


@router.put("/games/{game_id}/score")
async def update_game_score(
    game_id: str,
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db)
):
    db.table("educational_games").update({
        "score": body.get("score", 0),
        "completed": True
    }).eq("id", game_id).eq("student_id", current_user["id"]).execute()
    return {"message": "تم حفظ النتيجة"}


# ============================================
# التقدم والإحصائيات
# ============================================
@router.get("/progress")
async def get_progress(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    user_id = current_user["id"]

    streak = db.table("streaks").select("*").eq("user_id", user_id).execute()
    streak_data = streak.data[0] if streak.data else {}

    convs = db.table("ai_conversations").select("id", count="exact").eq("student_id", user_id).execute()

    games = db.table("educational_games").select("score, completed").eq("student_id", user_id).execute()
    completed_games = [g for g in (games.data or []) if g.get("completed")]
    avg_score = sum(g["score"] for g in completed_games) / len(completed_games) if completed_games else 0

    test_res = db.table("test_results").select("score").eq("student_id", user_id).execute()
    avg_test = sum(r["score"] for r in (test_res.data or []) if r.get("score")) / max(len(test_res.data or []), 1)

    return {
        "streak": streak_data.get("current_streak", 0),
        "longest_streak": streak_data.get("longest_streak", 0),
        "total_stars": streak_data.get("total_stars", 0),
        "learning_style": current_user.get("learning_style"),
        "total_conversations": len(convs.data or []),
        "total_games_played": len(completed_games),
        "avg_game_score": round(avg_score, 1),
        "avg_test_score": round(avg_test, 1),
        "total_tests": len(test_res.data or []),
    }


# ============================================
# الشكاوى والاقتراحات
# ============================================
@router.post("/complaints")
async def submit_complaint(
    complaint: ComplaintCreate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    db.table("complaints").insert({
        "user_id": current_user["id"],
        "school_id": current_user.get("school_id"),
        "type": complaint.type,
        "title": complaint.title,
        "content": complaint.content,
    }).execute()
    return {"message": "تم إرسال شكواك بنجاح. شكراً لك!"}
