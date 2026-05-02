# راوتر لوحة المدير
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.models.schemas import SchoolSetupRequest, StatsResponse
from app.services.account_generator import generate_accounts
from app.auth import get_current_user
from app.database import get_db
import io
import csv
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/manager", tags=["المدير"])


def require_manager(current_user: dict = Depends(get_current_user)):
    """التحقق من دور المدير"""
    if current_user["role"] not in ("manager", "admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة للمديرين فقط"
        )
    return current_user


@router.get("/schools")
async def get_schools(
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """جلب قائمة المدارس"""
    result = db.table("schools").select("*").execute()
    return result.data


@router.post("/setup")
async def setup_school(
    request: SchoolSetupRequest,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """إعداد المدرسة وتوليد الحسابات"""

    # التحقق من وجود المدرسة
    school = db.table("schools").select("*").eq("id", request.school_id).execute()
    if not school.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المدرسة غير موجودة"
        )

    school_name = school.data[0]["name"]

    # توليد الحسابات
    accounts = await generate_accounts(
        school_id=request.school_id,
        students=request.students,
        teachers=request.teachers,
        admins_count=request.admins_count,
        db=db
    )

    # حفظ بيانات الإعداد مع الباسووردات
    db.table("school_setup").upsert({
        "school_id": request.school_id,
        "students_data": request.students,
        "teachers_data": request.teachers,
        "admins_count": request.admins_count,
        "total_accounts_generated": len(accounts),
        "passwords_data": accounts  # حفظ كل بيانات الحسابات بما فيها الباسوورد
    }).execute()

    # تحديث حالة المدرسة
    db.table("schools").update({"setup_completed": True}).eq("id", request.school_id).execute()

    return {
        "accounts": accounts,
        "total": len(accounts),
        "school_name": school_name
    }


@router.get("/accounts/{school_id}")
async def get_accounts(
    school_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """جلب جميع حسابات مدرسة"""
    result = db.table("users") \
        .select("id, email, role, full_name, grade, subject, ministry_id, is_active, created_at") \
        .eq("school_id", school_id) \
        .neq("role", "manager") \
        .execute()

    return result.data


@router.get("/export/{school_id}")
async def export_accounts_csv(
    school_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """تحميل الحسابات كملف CSV مع دعم العربي"""

    result = db.table("users") \
        .select("full_name, email, role, grade, subject, ministry_id") \
        .eq("school_id", school_id) \
        .neq("role", "manager") \
        .execute()

    # إنشاء CSV مع BOM للعربي
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["الاسم الكامل", "الإيميل", "الدور", "الصف", "المادة", "الرقم الوزاري"])
    for user in result.data:
        role_ar = {"student": "طالب", "teacher": "معلم", "admin": "إداري"}.get(user["role"], user["role"])
        writer.writerow([
            user.get("full_name", ""),
            user.get("email", ""),
            role_ar,
            user.get("grade", ""),
            user.get("subject", ""),
            user.get("ministry_id", ""),
        ])

    csv_content = "﻿" + output.getvalue()  # BOM للعربي

    school = db.table("schools").select("name").eq("id", school_id).execute()
    school_name = school.data[0]["name"] if school.data else "school"

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="morix_accounts_{school_name}.csv"'}
    )


@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """لوحة الإحصائيات"""

    school_id = current_user.get("school_id")

    # إجمالي المستخدمين
    users_query = db.table("users").select("role, learning_style", count="exact")
    if school_id:
        users_query = users_query.eq("school_id", school_id)
    users = users_query.execute()

    total_users = len(users.data)
    students = [u for u in users.data if u["role"] == "student"]
    teachers = [u for u in users.data if u["role"] == "teacher"]
    admins = [u for u in users.data if u["role"] == "admin"]

    # أساليب التعلم
    learning_styles = {"visual": 0, "auditory": 0, "kinesthetic": 0, "unknown": 0}
    for s in students:
        style = s.get("learning_style") or "unknown"
        learning_styles[style] = learning_styles.get(style, 0) + 1

    # عدد المحادثات
    convs = db.table("ai_conversations").select("id", count="exact").execute()
    total_conversations = len(convs.data)

    # تسجيلات الدخول الأخيرة (7 أيام)
    from datetime import datetime, timedelta, timezone
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    logins = db.table("analytics") \
        .select("id") \
        .eq("event_type", "login") \
        .gt("created_at", week_ago) \
        .execute()

    return {
        "total_users": total_users,
        "total_students": len(students),
        "total_teachers": len(teachers),
        "total_admins": len(admins),
        "total_conversations": total_conversations,
        "learning_styles": learning_styles,
        "recent_logins": len(logins.data)
    }


@router.get("/passwords/{school_id}")
async def get_saved_passwords(
    school_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """جلب الباسووردات المحفوظة للمدير"""
    result = db.table("school_setup") \
        .select("passwords_data, total_accounts_generated, updated_at") \
        .eq("school_id", school_id) \
        .execute()

    if not result.data or not result.data[0].get("passwords_data"):
        return {"accounts": [], "total": 0}

    return {
        "accounts": result.data[0]["passwords_data"],
        "total": result.data[0]["total_accounts_generated"],
        "generated_at": result.data[0]["updated_at"]
    }


@router.get("/books")
async def get_books(
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """جلب كتب المنهج"""
    result = db.table("curriculum_books").select("*").eq("is_active", True).execute()
    return result.data


@router.post("/books")
async def add_book(
    book_data: dict,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db)
):
    """إضافة كتاب منهجي جديد"""
    from app.services.book_summarizer import summarize_book

    title = book_data.get("title", "")
    subject = book_data.get("subject", "")
    raw_text = book_data.get("raw_text", "")

    summary = None
    if raw_text:
        summary = await summarize_book(title, subject, raw_text)

    result = db.table("curriculum_books").insert({
        "title": title,
        "subject": subject,
        "grade": book_data.get("grade", ""),
        "summary": summary,
        "key_concepts": book_data.get("key_concepts", []),
        "is_active": True
    }).execute()

    return result.data[0] if result.data else {"message": "تم إضافة الكتاب"}


# ============================================================
# 👔 ميزات المدير المتقدمة
# ============================================================

@router.post("/schools")
async def create_school(
    body: dict,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db),
):
    """إضافة مدرسة جديدة (تنحفظ بشكل دائم في قاعدة البيانات)"""
    import uuid as _uuid
    name = (body.get("name") or "").strip()
    branch = (body.get("branch") or "").strip()
    ministry_code = (body.get("ministry_code") or "").strip()

    if not name:
        raise HTTPException(400, "اكتب اسم المدرسة")

    full_name = f"{name} - فرع {branch}" if branch else name

    # تأكد إن المدرسة مش مكررة
    existing = db.table("schools").select("id").eq("name", full_name).execute()
    if existing.data:
        raise HTTPException(400, "مدرسة بنفس الاسم والفرع موجودة بالفعل")

    # توليد كود وزاري تلقائي لو فاضي (الـ DB قد تكون بـ UNIQUE NOT NULL)
    if not ministry_code:
        ministry_code = f"MX-{_uuid.uuid4().hex[:8].upper()}"

    # محاولات تدريجية: مع كل الأعمدة، بدون branch، بدون كل الإضافات
    attempts = [
        {"name": full_name, "ministry_code": ministry_code, "branch": branch or None, "setup_completed": False},
        {"name": full_name, "ministry_code": ministry_code, "setup_completed": False},
        {"name": full_name, "ministry_code": ministry_code},
    ]

    last_error = None
    for payload in attempts:
        try:
            result = db.table("schools").insert(payload).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            last_error = e
            continue

    raise HTTPException(500, f"تعذرت إضافة المدرسة: {last_error}")


@router.delete("/schools/{school_id}")
async def delete_school(
    school_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db),
):
    """حذف مدرسة + كل حساباتها نهائياً"""
    try:
        db.table("users").delete().eq("school_id", school_id).execute()
    except Exception:
        pass
    try:
        db.table("school_setup").delete().eq("school_id", school_id).execute()
    except Exception:
        pass
    db.table("schools").delete().eq("id", school_id).execute()
    return {"message": "✅ تم حذف المدرسة وكل حساباتها"}


@router.post("/upload-excel")
async def upload_excel_setup(
    school_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_manager),
    db=Depends(get_db),
):
    """
    رفع ملف Excel لإعداد المدرسة.
    الأعمدة المتوقعة (مرنة):
      - الاسم / Name / full_name
      - الدور / Role / role  (student / teacher / admin / طالب / معلم / إداري)
      - الصف / Grade / grade  (للطالب)
      - المادة / Subject / subject  (للمعلم)
      - الرقم الوزاري / Ministry ID / ministry_id  (اختياري)
    """
    from openpyxl import load_workbook
    from app.services.account_generator import generate_accounts

    school = db.table("schools").select("*").eq("id", school_id).execute()
    if not school.data:
        raise HTTPException(404, "المدرسة غير موجودة")

    content = await file.read()
    try:
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
    except Exception as e:
        raise HTTPException(400, f"تعذرت قراءة ملف Excel: {e}")

    rows = list(ws.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        raise HTTPException(400, "الملف فارغ")

    headers = [str(h or "").strip().lower() for h in rows[0]]

    def find_col(*candidates):
        for c in candidates:
            for i, h in enumerate(headers):
                if c in h:
                    return i
        return -1

    col_name = find_col("اسم", "name", "full_name")
    col_role = find_col("دور", "role")
    col_grade = find_col("صف", "grade", "صفّ")
    col_subject = find_col("مادة", "subject")
    col_ministry = find_col("وزاري", "ministry", "id")

    if col_name == -1 or col_role == -1:
        raise HTTPException(400, "الملف لازم يحتوي على عمودين على الأقل: الاسم والدور")

    students, teachers, admins_count = [], [], 0
    role_map = {
        "طالب": "student", "student": "student",
        "معلم": "teacher", "معلّم": "teacher", "teacher": "teacher",
        "اداري": "admin", "إداري": "admin", "admin": "admin",
    }

    for row in rows[1:]:
        if not row or all(c is None for c in row):
            continue
        full_name = str(row[col_name] or "").strip()
        if not full_name:
            continue
        raw_role = str(row[col_role] or "").strip().lower()
        role = role_map.get(raw_role, "student")
        grade = str(row[col_grade] or "").strip() if col_grade != -1 else ""
        subject = str(row[col_subject] or "").strip() if col_subject != -1 else ""
        ministry_id = str(row[col_ministry] or "").strip() if col_ministry != -1 else ""

        entry = {"full_name": full_name}
        if ministry_id:
            entry["ministry_id"] = ministry_id

        if role == "student":
            entry["grade"] = grade or "غير محدد"
            students.append(entry)
        elif role == "teacher":
            entry["subject"] = subject or "عام"
            teachers.append(entry)
        elif role == "admin":
            admins_count += 1

    accounts = await generate_accounts(
        school_id=school_id,
        students=students,
        teachers=teachers,
        admins_count=admins_count,
        db=db,
    )

    db.table("school_setup").upsert({
        "school_id": school_id,
        "students_data": students,
        "teachers_data": teachers,
        "admins_count": admins_count,
        "total_accounts_generated": len(accounts),
        "passwords_data": accounts,
    }).execute()

    db.table("schools").update({"setup_completed": True}).eq("id", school_id).execute()

    return {
        "accounts": accounts,
        "total": len(accounts),
        "school_name": school.data[0]["name"],
        "students_count": len(students),
        "teachers_count": len(teachers),
        "admins_count": admins_count,
    }


@router.get("/account-password/{user_id}")
async def get_account_password(
    user_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db),
):
    """عرض كلمة سر حساب معين (للمدير فقط)"""
    user = db.table("users").select("school_id, email, full_name").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(404, "الحساب غير موجود")

    school_id = user.data[0]["school_id"]
    email = user.data[0]["email"]

    setup = db.table("school_setup").select("passwords_data").eq("school_id", school_id).execute()
    if not setup.data or not setup.data[0].get("passwords_data"):
        raise HTTPException(404, "كلمات السر غير محفوظة لهذه المدرسة")

    accounts = setup.data[0]["passwords_data"]
    for acc in accounts:
        if acc.get("email") == email:
            return {
                "email": email,
                "password": acc.get("password"),
                "full_name": user.data[0]["full_name"],
            }
    raise HTTPException(404, "كلمة السر غير موجودة لهذا الحساب")


@router.delete("/accounts/{user_id}")
async def delete_account(
    user_id: str,
    current_user: dict = Depends(require_manager),
    db=Depends(get_db),
):
    """حذف حساب نهائياً من قاعدة البيانات (مع كل بياناته)"""
    user = db.table("users").select("id, school_id, email, role").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(404, "الحساب غير موجود")

    if user.data[0].get("role") in ("manager", "owner"):
        raise HTTPException(403, "لا يمكن حذف حسابات المديرين أو الملاك من هنا")

    email = user.data[0]["email"]
    school_id = user.data[0]["school_id"]

    # حذف كل البيانات المرتبطة بالحساب
    related_tables = [
        "ai_conversations", "ai_messages", "messages", "conversations",
        "homework", "tests", "worksheets", "submissions",
        "diagnostic_results", "streaks", "achievements",
        "user_settings", "analytics", "complaints",
    ]
    for tbl in related_tables:
        try:
            db.table(tbl).delete().eq("user_id", user_id).execute()
        except Exception:
            pass
        try:
            db.table(tbl).delete().eq("student_id", user_id).execute()
        except Exception:
            pass

    # حذف الحساب من users
    db.table("users").delete().eq("id", user_id).execute()

    # حذف من school_setup.passwords_data
    try:
        setup = db.table("school_setup").select("passwords_data").eq("school_id", school_id).execute()
        if setup.data and setup.data[0].get("passwords_data"):
            new_pw = [a for a in setup.data[0]["passwords_data"] if a.get("email") != email]
            db.table("school_setup").update({"passwords_data": new_pw}).eq("school_id", school_id).execute()
    except Exception:
        pass

    return {"message": f"✅ تم حذف الحساب {email} نهائياً مع كل بياناته"}


# ============================================================
# ⚙️ إعدادات المدير
# ============================================================
@router.get("/settings")
async def get_manager_settings(current_user: dict = Depends(require_manager), db=Depends(get_db)):
    result = db.table("user_settings").select("*").eq("user_id", current_user["id"]).execute()
    base = {
        "theme": "dark", "brightness": 100, "language": "ar",
        "notifications_enabled": True,
        "avatar_url": current_user.get("avatar_url", ""),
        "email": current_user.get("email", ""),
        "full_name": current_user.get("full_name", ""),
    }
    if not result.data: return base
    s = result.data[0]
    return {**base, **{k: v for k, v in s.items() if k not in ("id","user_id","created_at","updated_at")}, "avatar_url": current_user.get("avatar_url", "")}


@router.put("/settings")
async def update_manager_settings(body: dict, current_user: dict = Depends(require_manager), db=Depends(get_db)):
    valid_langs = {"ar", "en", "de", "fr", "zh", "es"}
    valid_themes = {"dark", "light", "library"}
    theme = body.get("theme", "dark")
    if theme not in valid_themes: theme = "dark"
    lang = body.get("language", "ar")
    if lang not in valid_langs: lang = "ar"
    try: brightness = max(20, min(100, int(body.get("brightness", 100))))
    except: brightness = 100
    data = {
        "user_id": current_user["id"], "theme": theme, "brightness": brightness,
        "language": lang, "notifications_enabled": bool(body.get("notifications_enabled", True)),
    }
    try:
        existing = db.table("user_settings").select("id").eq("user_id", current_user["id"]).execute()
        if existing.data:
            db.table("user_settings").update(data).eq("user_id", current_user["id"]).execute()
        else:
            db.table("user_settings").insert(data).execute()
    except Exception as e:
        logger.warning(f"Manager settings save failed: {e}")
    if body.get("avatar_url") is not None:
        try: db.table("users").update({"avatar_url": body["avatar_url"]}).eq("id", current_user["id"]).execute()
        except: pass
    return {"message": "✅ تم حفظ الإعدادات"}


@router.post("/strategic-advisor")
async def strategic_advisor(
    body: dict,
    current_user: dict = Depends(require_manager),
):
    """مستشار استراتيجي ذكي"""
    question = (body.get("question") or "").strip()
    context = body.get("context", "")
    if not question:
        raise HTTPException(400, "اطرح سؤالك الاستراتيجي")
    from app.services.ai_service import chat_with_gemini
    prompt = f"""أنت مستشار استراتيجي تعليمي خبير.
سياق المستخدم: {context or 'مدير مدارس متعددة'}
السؤال: {question}

قدم استشارة استراتيجية شاملة:
1. تحليل الموقف
2. 3 خيارات استراتيجية مع إيجابيات/سلبيات
3. التوصية النهائية مع خطة تنفيذ مرحلية
4. مؤشرات نجاح قابلة للقياس (KPIs)"""
    try:
        text, _ = await chat_with_gemini(prompt, None, full_name=current_user.get("full_name", ""), role="manager")
        return {"advice": text}
    except Exception:
        return {"advice": "تعذر الاتصال بـ AI"}


@router.get("/health-score")
async def franchise_health(current_user: dict = Depends(require_manager), db=Depends(get_db)):
    """درجة صحية شاملة لكل المدارس"""
    from datetime import datetime, timedelta, timezone
    week = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    scored = []
    try:
        schools = db.table("schools").select("id, name, setup_completed").execute()
        for sc in (schools.data or []):
            try:
                users = db.table("users").select("id").eq("school_id", sc["id"]).execute()
                total = len(users.data or [])
            except Exception:
                total = 0

            if total == 0:
                scored.append({"school_id": sc["id"], "name": sc["name"], "score": 20, "status": "🔴 فارغة", "users": 0, "active_week": 0})
                continue

            active = 0
            try:
                ull = db.table("users").select("last_login").eq("school_id", sc["id"]).execute()
                active = sum(1 for u in (ull.data or []) if u.get("last_login") and str(u["last_login"]) >= week)
            except Exception:
                pass
            if active == 0:
                try:
                    logs = db.table("analytics").select("student_id").eq("school_id", sc["id"]).eq("event_type", "login").gte("created_at", week).execute()
                    active = len(set(l.get("student_id") for l in (logs.data or []) if l.get("student_id")))
                except Exception:
                    pass

            engagement = (active / total) * 100
            score = int(engagement * 0.6 + (40 if sc.get("setup_completed") else 0))
            status_label = "🟢 ممتازة" if score >= 75 else "🟡 جيدة" if score >= 50 else "🟠 ضعيفة" if score >= 25 else "🔴 حرجة"
            scored.append({"school_id": sc["id"], "name": sc["name"], "score": score, "status": status_label, "users": total, "active_week": active})
    except Exception as e:
        logger.error(f"Health failed: {e}")
    return sorted(scored, key=lambda x: -x["score"])
