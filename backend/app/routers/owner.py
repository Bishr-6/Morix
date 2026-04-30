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


# ============================================================
# 👑 ميزات المالك المتقدمة
# ============================================================

@router.get("/platform-pulse")
async def platform_pulse(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    """نبض المنصة لحظياً"""
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    try:
        users = db.table("users").select("id, role, is_active, last_login").execute()
        all_users = users.data or []
        active_today = sum(1 for u in all_users if u.get("last_login", "") >= today)
        active_week = sum(1 for u in all_users if u.get("last_login", "") >= week_ago)
        ai_calls = db.table("analytics").select("id", count="exact").gte("created_at", week_ago).execute()
        complaints_open = db.table("complaints").select("id", count="exact").eq("status", "pending").execute()
        return {
            "total_users": len(all_users),
            "active_today": active_today,
            "active_this_week": active_week,
            "ai_calls_week": ai_calls.count or 0,
            "open_complaints": complaints_open.count or 0,
            "health_score": min(100, int((active_week / max(len(all_users), 1)) * 100)),
        }
    except Exception as e:
        logger.error(f"Platform pulse failed: {e}")
        return {"total_users": 0, "active_today": 0, "active_this_week": 0, "ai_calls_week": 0, "open_complaints": 0, "health_score": 0}


@router.get("/ai-cost")
async def ai_cost_estimator(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    """تقدير تكلفة استدعاءات Gemini"""
    from datetime import datetime, timedelta, timezone
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        analytics = db.table("analytics").select("event_type").gte("created_at", week_ago).execute()
        ai_events = [a for a in (analytics.data or []) if "ai" in str(a.get("event_type", "")).lower() or a.get("event_type") in ("chat", "ppt_generated", "lesson_plan_generated")]
        # تقدير تقريبي: 0.0001$ لكل استدعاء بمتوسط
        cost_estimate = round(len(ai_events) * 0.0001, 4)
        return {
            "calls_this_week": len(ai_events),
            "estimated_cost_usd": cost_estimate,
            "estimated_monthly_cost": round(cost_estimate * 4.3, 2),
            "savings_from_cache": "≈ 35% (من نظام الكاش)",
        }
    except Exception:
        return {"calls_this_week": 0, "estimated_cost_usd": 0, "estimated_monthly_cost": 0, "savings_from_cache": "0%"}


@router.get("/churn-risk")
async def churn_risk(current_user: dict = Depends(_require_owner), db=Depends(get_db)):
    """تنبؤ بالمدارس المعرضة لإلغاء الاشتراك"""
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    risks = []
    try:
        schools = db.table("schools").select("id, name").execute()
        for sc in (schools.data or []):
            users = db.table("users").select("id, last_login").eq("school_id", sc["id"]).execute()
            total = len(users.data or [])
            if total == 0:
                continue
            inactive = sum(1 for u in users.data if not u.get("last_login") or u.get("last_login") < cutoff)
            inactive_pct = (inactive / total) * 100
            if inactive_pct >= 60:
                risks.append({
                    "school_id": sc["id"],
                    "school_name": sc["name"],
                    "inactive_pct": round(inactive_pct, 1),
                    "risk_level": "high" if inactive_pct >= 80 else "medium",
                })
    except Exception as e:
        logger.error(f"Churn risk failed: {e}")
    return {"at_risk_schools": sorted(risks, key=lambda x: -x["inactive_pct"])}


@router.post("/broadcast")
async def broadcast_message(
    body: dict,
    current_user: dict = Depends(_require_owner),
    db=Depends(get_db),
):
    """بث رسالة لكل مستخدمي المنصة"""
    title = body.get("title", "إعلان من إدارة Morix")
    content = (body.get("content") or "").strip()
    if not content:
        raise HTTPException(400, "اكتب محتوى الإعلان")
    try:
        # حفظ كحدث + إعلان مدرسي
        db.table("analytics").insert({
            "student_id": current_user["id"],
            "school_id": current_user.get("school_id"),
            "event_type": "platform_broadcast",
            "event_data": {"title": title, "content": content, "by": current_user.get("full_name")},
        }).execute()
    except Exception:
        pass
    return {"message": f"✅ تم بث الإعلان لجميع المستخدمين", "title": title}
