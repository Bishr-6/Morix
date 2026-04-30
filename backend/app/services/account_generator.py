# توليد الحسابات تلقائياً
import random
import string
from typing import List
from app.config import settings
from app.auth import hash_password
import re


def generate_password(length: int = 10) -> str:
    """توليد كلمة مرور عشوائية"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def normalize_arabic_name(name: str) -> str:
    """تحويل الاسم العربي لصيغة إيميل"""
    arabic_to_latin = {
        'أ': 'a', 'ا': 'a', 'إ': 'a', 'آ': 'a',
        'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
        'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dh',
        'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
        'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
        'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
        'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
        'ة': 'a', 'ء': 'a', 'ئ': 'a', 'ؤ': 'w',
        ' ': '.', '-': '.', '_': '.'
    }
    result = ""
    for char in name:
        result += arabic_to_latin.get(char, char)
    # إزالة الأحرف غير المسموح بها في الإيميل
    result = re.sub(r'[^a-zA-Z0-9.]', '', result)
    result = re.sub(r'\.+', '.', result)
    result = result.strip('.')
    return result.lower() or "user"


def generate_student_email(name: str, ministry_id: str) -> str:
    """توليد إيميل الطالب: morix{رقم_وزاري}@morix.tech"""
    mid = re.sub(r'[^a-zA-Z0-9]', '', str(ministry_id)) or "000"
    return f"morix{mid}@{settings.allowed_email_domain}"


def generate_teacher_email(subject: str, index: int, ministry_id: str = "") -> str:
    """توليد إيميل المعلم: morix{رقم_وزاري}@morix.tech أو morix.teacher{رقم}@morix.tech"""
    if ministry_id:
        mid = re.sub(r'[^a-zA-Z0-9]', '', str(ministry_id))
        if mid:
            return f"morix{mid}@{settings.allowed_email_domain}"
    return f"morix.teacher{index}@{settings.allowed_email_domain}"


def generate_admin_email(index: int, ministry_id: str = "") -> str:
    """توليد إيميل الإداري: morix{رقم_وزاري}@morix.tech أو morix.admin{رقم}@morix.tech"""
    if ministry_id:
        mid = re.sub(r'[^a-zA-Z0-9]', '', str(ministry_id))
        if mid:
            return f"morix{mid}@{settings.allowed_email_domain}"
    return f"morix.admin{index}@{settings.allowed_email_domain}"


async def generate_accounts(
    school_id: str,
    students: List[dict],
    teachers: List[dict],
    admins_count: int,
    db,
    manager_id: str = None
) -> List[dict]:
    """توليد جميع الحسابات وحفظها في قاعدة البيانات"""
    all_accounts = []

    # توليد حسابات الطلبة
    for student in students:
        password = generate_password()
        email = generate_student_email(student.get("name", ""), student.get("ministry_id", "000"))

        # التحقق من عدم تكرار الإيميل
        existing = db.table("users").select("id").eq("email", email).execute()
        if existing.data:
            suffix = random.randint(100, 999)
            email = email.replace("@", f"{suffix}@")

        account_data = {
            "email": email,
            "password_hash": hash_password(password),
            "role": "student",
            "full_name": student.get("name", ""),
            "ministry_id": student.get("ministry_id", ""),
            "grade": student.get("grade", ""),
            "school_id": school_id,
            "is_active": True,
            "must_change_password": True,
        }

        db.table("users").insert(account_data).execute()
        all_accounts.append({
            "full_name": student.get("name", ""),
            "email": email,
            "password": password,
            "role": "student",
            "grade": student.get("grade", ""),
            "ministry_id": student.get("ministry_id", ""),
        })

    # توليد حسابات المعلمين
    for i, teacher in enumerate(teachers, start=1):
        password = generate_password()
        email = generate_teacher_email(teacher.get("subject", ""), i, teacher.get("ministry_id", ""))

        existing = db.table("users").select("id").eq("email", email).execute()
        if existing.data:
            suffix = random.randint(100, 999)
            email = email.replace("@", f"{suffix}@")

        account_data = {
            "email": email,
            "password_hash": hash_password(password),
            "role": "teacher",
            "full_name": teacher.get("name", ""),
            "subject": teacher.get("subject", ""),
            "school_id": school_id,
            "is_active": True,
            "must_change_password": True,
        }

        db.table("users").insert(account_data).execute()
        all_accounts.append({
            "full_name": teacher.get("name", ""),
            "email": email,
            "password": password,
            "role": "teacher",
            "subject": teacher.get("subject", ""),
        })

    # توليد حسابات الإداريين
    # نجيب أعلى رقم إداري موجود
    existing_admins = db.table("users") \
        .select("email") \
        .eq("school_id", school_id) \
        .eq("role", "admin") \
        .execute()
    start_index = len(existing_admins.data) + 1 if existing_admins.data else 1

    for i in range(start_index, start_index + admins_count):
        password = generate_password()
        email = generate_admin_email(i)

        existing = db.table("users").select("id").eq("email", email).execute()
        if existing.data:
            email = generate_admin_email(i + 100)

        account_data = {
            "email": email,
            "password_hash": hash_password(password),
            "role": "admin",
            "full_name": f"إداري {i}",
            "school_id": school_id,
            "is_active": True,
            "must_change_password": True,
        }

        db.table("users").insert(account_data).execute()
        all_accounts.append({
            "full_name": f"إداري {i}",
            "email": email,
            "password": password,
            "role": "admin",
        })

    return all_accounts
