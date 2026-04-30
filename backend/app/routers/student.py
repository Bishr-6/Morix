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


# ============================================
# 🏆 لوحة المتصدرين
# ============================================
@router.get("/leaderboard")
async def get_leaderboard(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    school_id = current_user.get("school_id")
    query = db.table("users").select(
        "id, full_name, avatar_url, grade, stars_count, streak_count"
    ).eq("role", "student").eq("is_active", True)
    if school_id:
        query = query.eq("school_id", school_id)
    result = query.order("stars_count", desc=True).limit(10).execute()
    leaders = []
    for i, u in enumerate(result.data or []):
        leaders.append({
            "rank": i + 1,
            "id": u["id"],
            "full_name": u.get("full_name", ""),
            "avatar_url": u.get("avatar_url"),
            "grade": u.get("grade", ""),
            "stars_count": u.get("stars_count", 0) or 0,
            "streak_count": u.get("streak_count", 0) or 0,
            "is_me": u["id"] == current_user["id"],
        })
    return leaders


# ============================================
# 🎯 التحدي اليومي
# ============================================
@router.get("/daily-challenge")
async def get_daily_challenge(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    today = date.today().isoformat()
    try:
        existing = db.table("analytics").select("event_data").eq(
            "student_id", current_user["id"]
        ).eq("event_type", "daily_challenge").gte("created_at", today).execute()
        if existing.data:
            return {"already_answered": True, "result": existing.data[0]["event_data"]}
    except Exception:
        pass
    import random
    subjects = ["الرياضيات", "العلوم", "اللغة العربية", "الفيزياء", "الكيمياء", "التاريخ", "الجغرافيا", "الأحياء"]
    subject = random.choice(subjects)
    try:
        from app.services.ai_service import generate_game_content
        content = await generate_game_content("mcq", subject, "")
        if content and content.get("items"):
            q = content["items"][0]
            return {"already_answered": False, "question": q, "subject": subject}
    except Exception as e:
        logger.error(f"Daily challenge gen failed: {e}")
    return {"already_answered": False, "question": None, "subject": subject}


@router.post("/daily-challenge/answer")
async def answer_daily_challenge(
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db),
):
    correct = bool(body.get("correct", False))
    stars_earned = 25 if correct else 5
    try:
        streak = db.table("streaks").select("*").eq("user_id", current_user["id"]).execute()
        if streak.data:
            current_stars = streak.data[0].get("total_stars", 0) or 0
            new_total = current_stars + stars_earned
            db.table("streaks").update({"total_stars": new_total}).eq("user_id", current_user["id"]).execute()
            db.table("users").update({"stars_count": new_total}).eq("id", current_user["id"]).execute()
    except Exception:
        pass
    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "daily_challenge",
            "event_data": {"correct": correct, "stars_earned": stars_earned},
        }).execute()
    except Exception:
        pass
    return {
        "stars_earned": stars_earned,
        "message": f"✅ أحسنت! كسبت {stars_earned} نجمة!" if correct else f"💪 كسبت {stars_earned} نجمة على المحاولة، حاول غداً!",
    }


# ============================================
# 😊 متتبع الحالة المزاجية + نصائح ذكية
# ============================================
@router.post("/mood")
async def log_mood(
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db),
):
    mood = body.get("mood", "neutral")
    note = body.get("note", "")
    suggestions = {
        "happy":   "🌟 أنت في قمة طاقتك! استغل هذا الوقت في حل اختبار صعب.",
        "focused": "🎯 تركيزك ممتاز! ابدأ جلسة بومودورو 25 دقيقة الآن.",
        "tired":   "😴 خذ استراحة قصيرة، شاهد فيديو تعليمي خفيف بدل القراءة.",
        "stressed":"🧘 تنفس بعمق. جرب البطاقات التعليمية لمراجعة سريعة بدون ضغط.",
        "bored":   "🎮 العب لعبة تعليمية تفاعلية لإحياء حماسك!",
        "neutral": "📚 ابدأ بمراجعة موضوع تحبه قبل الانتقال للصعب.",
    }
    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "mood_tracker",
            "event_data": {"mood": mood, "note": note},
        }).execute()
    except Exception:
        pass
    return {"suggestion": suggestions.get(mood, suggestions["neutral"]), "mood": mood}


@router.get("/mood/history")
async def mood_history(current_user: dict = Depends(_require_student), db=Depends(get_db)):
    try:
        res = db.table("analytics").select("event_data, created_at").eq(
            "student_id", current_user["id"]
        ).eq("event_type", "mood_tracker").order("created_at", desc=True).limit(7).execute()
        return res.data or []
    except Exception:
        return []


# ============================================
# ⏱️ تسجيل جلسات بومودورو
# ============================================
@router.post("/focus-session")
async def log_focus_session(
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db),
):
    duration = int(body.get("duration_minutes", 25))
    technique = body.get("technique", "pomodoro")
    bonus_stars = 2 if duration >= 25 else 1
    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "focus_session",
            "event_data": {"duration_minutes": duration, "technique": technique, "stars": bonus_stars},
        }).execute()
        streak = db.table("streaks").select("*").eq("user_id", current_user["id"]).execute()
        if streak.data:
            cur = streak.data[0].get("total_stars", 0) or 0
            db.table("streaks").update({"total_stars": cur + bonus_stars}).eq("user_id", current_user["id"]).execute()
            db.table("users").update({"stars_count": cur + bonus_stars}).eq("id", current_user["id"]).execute()
    except Exception:
        pass
    return {"stars_earned": bonus_stars, "message": f"🎉 رائع! أكملت {duration} دقيقة تركيز وكسبت {bonus_stars} نجمة!"}


# ============================================
# 🧠 شخصية المعلم الذكي
# ============================================
TUTOR_PERSONALITIES = {
    "friend":   {"name": "صديق مرح", "emoji": "😄", "style": "ودود، يستخدم النكات والأمثلة من الحياة اليومية"},
    "strict":   {"name": "أستاذ صارم", "emoji": "🎓", "style": "رسمي، دقيق، يركز على القواعد والمفاهيم العلمية"},
    "coach":    {"name": "مدرب تحفيزي", "emoji": "💪", "style": "متحمس، يستخدم لغة رياضية، يحفزك دائماً"},
    "scientist":{"name": "عالم فضولي", "emoji": "🔬", "style": "يحب الاستكشاف، يطرح أسئلة مفتوحة، يربط بالعلم"},
}


@router.get("/tutor-personalities")
async def list_tutor_personalities(current_user: dict = Depends(_require_student)):
    return [{"key": k, **v} for k, v in TUTOR_PERSONALITIES.items()]


@router.post("/tutor-personality")
async def set_tutor_personality(
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db),
):
    key = body.get("personality", "friend")
    if key not in TUTOR_PERSONALITIES:
        raise HTTPException(400, "شخصية غير معروفة")
    try:
        db.table("user_settings").upsert({
            "user_id": current_user["id"],
            "tutor_personality": key,
        }).execute()
    except Exception:
        pass
    return {"message": f"تم اختيار: {TUTOR_PERSONALITIES[key]['name']}", "personality": key}


# ============================================
# 🌅 التأمل اليومي
# ============================================
@router.post("/reflection")
async def save_reflection(
    body: dict,
    current_user: dict = Depends(_require_student),
    db=Depends(get_db),
):
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "اكتب تأملك")
    try:
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "reflection",
            "event_data": {"text": text},
        }).execute()
        streak = db.table("streaks").select("*").eq("user_id", current_user["id"]).execute()
        if streak.data:
            cur = streak.data[0].get("total_stars", 0) or 0
            db.table("streaks").update({"total_stars": cur + 3}).eq("user_id", current_user["id"]).execute()
            db.table("users").update({"stars_count": cur + 3}).eq("id", current_user["id"]).execute()
    except Exception:
        pass
    return {"stars_earned": 3, "message": "🌟 شكراً لمشاركتك تأملك اليومي! +3 نجوم"}
