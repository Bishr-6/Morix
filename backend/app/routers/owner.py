# راوتر المالك - Morix Platform
from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_user
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/owner", tags=["المالك"])


def _require_owner(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="هذه الصفحة للمالك فقط")
    return current_user


@router.get("/stats")
async def get_platform_stats(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    schools = db.table("schools").select("id, name, setup_completed").execute()
    users = db.table("users").select("role").execute()
    convs = db.table("ai_conversations").select("id", count="exact").execute()
    complaints = db.table("complaints").select("status").execute()

    role_counts = {}
    for u in (users.data or []):
        role_counts[u["role"]] = role_counts.get(u["role"], 0) + 1

    complaint_stats = {"pending": 0, "reviewed": 0, "resolved": 0}
    for c in (complaints.data or []):
        s = c.get("status", "pending")
        complaint_stats[s] = complaint_stats.get(s, 0) + 1

    return {
        "total_schools": len(schools.data or []),
        "setup_completed_schools": sum(1 for s in (schools.data or []) if s.get("setup_completed")),
        "schools": schools.data or [],
        "role_counts": role_counts,
        "total_users": len(users.data or []),
        "total_conversations": len(convs.data or []),
        "complaint_stats": complaint_stats,
    }


@router.get("/complaints")
async def get_all_complaints(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    result = db.table("complaints") \
        .select("*, users!user_id(full_name, role, email), schools!school_id(name)") \
        .order("created_at", desc=True).execute()
    return result.data


@router.put("/complaints/{complaint_id}")
async def respond_to_complaint(
    complaint_id: str,
    body: dict,
    current_user: dict = Depends(_require_owner),
    db=Depends(get_db)
):
    db.table("complaints").update({
        "status": body.get("status", "reviewed"),
        "response": body.get("response", "")
    }).eq("id", complaint_id).execute()
    return {"message": "تم تحديث الشكوى"}


@router.get("/users")
async def get_all_users(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    result = db.table("users") \
        .select("id, full_name, email, role, school_id, is_active, created_at, schools!school_id(name)") \
        .neq("role", "owner") \
        .order("created_at", desc=True).execute()
    return result.data


@router.put("/users/{user_id}/toggle")
async def toggle_user(user_id: str, current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    user = db.table("users").select("is_active").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    new_status = not user.data[0]["is_active"]
    db.table("users").update({"is_active": new_status}).eq("id", user_id).execute()
    return {"is_active": new_status}


@router.get("/schools")
async def get_all_schools(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    result = db.table("schools").select("*").order("name").execute()
    return result.data
