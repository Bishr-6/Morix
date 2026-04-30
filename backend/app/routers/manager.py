# راوتر لوحة المدير
from fastapi import APIRouter, HTTPException, Depends, status
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
