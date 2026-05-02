# نقطة الدخول الرئيسية - Morix Platform Backend
import warnings
warnings.filterwarnings("ignore", ".*bcrypt.*")
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, manager, student, ai, teacher, owner, admin
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Morix API",
    description="منصة Morix للتعلم الذكي - API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "https://morix.tech",
        "https://www.morix.tech",
        "https://morix-srqw.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(manager.router, prefix="/api/v1")
app.include_router(student.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(teacher.router, prefix="/api/v1")
app.include_router(owner.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Morix", "version": settings.app_version}


@app.get("/api/v1/system-check")
async def system_check():
    """فحص شامل لمكونات المنصة — استخدمه للتشخيص"""
    checks = {"timestamp": None, "checks": {}}
    from datetime import datetime, timezone
    checks["timestamp"] = datetime.now(timezone.utc).isoformat()

    # 1) Supabase
    try:
        from app.database import get_supabase
        db = get_supabase()
        r = db.table("users").select("id", count="exact").limit(1).execute()
        checks["checks"]["supabase"] = {"ok": True, "users_count": r.count}
    except Exception as e:
        checks["checks"]["supabase"] = {"ok": False, "error": str(e)[:200]}

    # 2) Gemini API key validity
    try:
        from app.services.ai_service import chat_with_gemini
        text, _ = await chat_with_gemini("ping", None, full_name="System")
        if "leaked" in text.lower() or "غير صالح" in text or "تعذر" in text:
            checks["checks"]["gemini"] = {"ok": False, "message": text[:300]}
        else:
            checks["checks"]["gemini"] = {"ok": True, "sample_reply": text[:100]}
    except Exception as e:
        checks["checks"]["gemini"] = {"ok": False, "error": str(e)[:200]}

    # 3) Env vars present
    checks["checks"]["env"] = {
        "supabase_url": bool(settings.supabase_url),
        "supabase_key": bool(settings.supabase_service_key or settings.supabase_anon_key),
        "gemini_key": bool(settings.gemini_api_key),
        "jwt_secret": bool(settings.jwt_secret_key and settings.jwt_secret_key != "memorix-default-secret"),
    }

    overall_ok = all([
        checks["checks"].get("supabase", {}).get("ok"),
        checks["checks"].get("gemini", {}).get("ok"),
        all(checks["checks"]["env"].values()),
    ])
    checks["overall"] = "✅ كل شيء شغّال" if overall_ok else "⚠️ في مشاكل"
    return checks


@app.get("/")
async def root():
    return {"message": "مرحباً بك في Morix API - منصة التعلم الذكي", "docs": "/docs", "system_check": "/api/v1/system-check"}


# ============================================================
# 🌐 Iframe Proxy — يحذف headers اللي بتمنع التضمين
# ============================================================
from fastapi import Request, Query
from fastapi.responses import Response, StreamingResponse
import httpx
from urllib.parse import urlparse, urljoin

ALLOWED_HOSTS = {
    "hindawi.org", "www.hindawi.org",
    "noor-book.com", "www.noor-book.com",
    "shamela.ws", "www.shamela.ws",
    "openlibrary.org", "www.openlibrary.org",
    "archive.org", "www.archive.org",
    "gutenberg.org", "www.gutenberg.org",
    "eric.ed.gov",
    "ar.wikibooks.org", "ar.wikipedia.org", "ar.wikisource.org",
    "books.google.com", "books.google.com.eg",
    "kotobati.org", "www.kotobati.org",
    "wdl.org", "www.wdl.org",
}

STRIP_HEADERS = {
    "x-frame-options", "content-security-policy",
    "content-security-policy-report-only", "frame-options",
    "cross-origin-opener-policy", "cross-origin-embedder-policy",
    "cross-origin-resource-policy", "permissions-policy",
}


@app.get("/api/v1/proxy")
async def iframe_proxy(url: str = Query(...), request: Request = None):
    """يجيب صفحة خارجية ويحذف headers اللي بتمنع التضمين في iframe"""
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if host not in ALLOWED_HOSTS:
            base_check = ".".join(host.split(".")[-2:]) if host else ""
            if base_check not in {"hindawi.org", "noor-book.com", "shamela.ws", "openlibrary.org",
                                   "archive.org", "gutenberg.org", "ed.gov", "wikibooks.org",
                                   "wikipedia.org", "wikisource.org", "google.com",
                                   "kotobati.org", "wdl.org"}:
                return Response(content=f"<html dir='rtl'><body style='font-family:sans-serif;padding:24px;background:#0f172a;color:#fff'><h2>🚫 هذا الموقع غير مدعوم في البروكسي</h2><p>{host}</p><p><a style='color:#6366f1' href='{url}' target='_blank'>افتح الموقع في تبويب جديد</a></p></body></html>",
                                media_type="text/html; charset=utf-8")
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            r = await client.get(url, headers={"User-Agent": ua, "Accept-Language": "ar,en;q=0.8"})
        ctype = r.headers.get("content-type", "text/html; charset=utf-8")
        body = r.content
        # نعدّل الـ HTML: نحذف meta CSP + نضيف base href
        if "text/html" in ctype.lower():
            try:
                text = body.decode(r.encoding or "utf-8", errors="replace")
                proxy_base = "/api/v1/proxy?url="
                origin = f"{parsed.scheme}://{parsed.netloc}"
                # نضيف base tag لجعل الروابط النسبية تشتغل
                base_tag = f'<base href="{origin}/">'
                if "<head>" in text.lower():
                    import re
                    text = re.sub(r"(?i)<head[^>]*>", lambda m: m.group(0) + base_tag, text, count=1)
                # حذف meta CSP
                text = re.sub(r'(?i)<meta[^>]*http-equiv\s*=\s*["\']content-security-policy["\'][^>]*>', "", text)
                text = re.sub(r'(?i)<meta[^>]*http-equiv\s*=\s*["\']x-frame-options["\'][^>]*>', "", text)
                # نحوّل الـ <a href> اللي يفتح في نفس الموقع لتمشي عبر الـ proxy
                def rewrite_link(m):
                    href = m.group(2)
                    if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                        return m.group(0)
                    full = urljoin(url, href)
                    return f'{m.group(1)}href="{proxy_base}{full}"'
                text = re.sub(r'(<a\s[^>]*?)href="([^"]+)"', rewrite_link, text)
                body = text.encode("utf-8")
                ctype = "text/html; charset=utf-8"
            except Exception as e:
                logging.warning(f"HTML rewrite failed: {e}")
        # حذف الـ headers الممنوعة
        out_headers = {}
        for k, v in r.headers.items():
            if k.lower() in STRIP_HEADERS or k.lower().startswith("set-cookie"):
                continue
            if k.lower() in ("content-encoding", "content-length", "transfer-encoding"):
                continue
            out_headers[k] = v
        out_headers["Content-Type"] = ctype
        out_headers["X-Frame-Options"] = "ALLOWALL"
        return Response(content=body, status_code=r.status_code, headers=out_headers, media_type=ctype)
    except Exception as e:
        logging.error(f"Proxy failed: {e}")
        return Response(
            content=f"<html dir='rtl'><body style='font-family:sans-serif;padding:24px;background:#0f172a;color:#fff'><h2>⚠️ تعذر تحميل الصفحة</h2><p>{str(e)[:200]}</p><p><a style='color:#6366f1' href='{url}' target='_blank'>افتح الرابط مباشرة</a></p></body></html>",
            media_type="text/html; charset=utf-8",
            status_code=200,
        )
