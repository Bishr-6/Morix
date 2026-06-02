# تخزين ملفات الكتب على Backblaze B2 (S3-compatible) عبر روابط موقّعة (presigned URLs)
# نستخدم توقيع AWS Signature V4 يدوياً (بدون boto3) لإبقاء حزمة النشر خفيفة على Vercel.
# لو مفاتيح B2 غير مضبوطة، الدوال ترجع None ليتمكن الكود من الرجوع تلقائياً لـ Supabase.
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from urllib.parse import quote
from app.config import settings

logger = logging.getLogger(__name__)

_SERVICE = "s3"


def is_configured() -> bool:
    """هل مفاتيح Backblaze B2 مضبوطة؟"""
    return bool(
        getattr(settings, "b2_key_id", "")
        and getattr(settings, "b2_app_key", "")
        and getattr(settings, "b2_bucket", "")
        and getattr(settings, "b2_endpoint", "")
    )


def _uri_encode(s: str, encode_slash: bool = True) -> str:
    safe = "-_.~" + ("" if encode_slash else "/")
    return quote(str(s), safe=safe)


def _host() -> str:
    ep = (settings.b2_endpoint or "").strip().replace("https://", "").replace("http://", "").rstrip("/")
    return ep


def _region() -> str:
    return (getattr(settings, "b2_region", "") or "").strip() or "us-east-005"


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(secret: str, datestamp: str, region: str) -> bytes:
    k_date = _hmac(("AWS4" + secret).encode("utf-8"), datestamp)
    k_region = _hmac(k_date, region)
    k_service = _hmac(k_region, _SERVICE)
    return _hmac(k_service, "aws4_request")


def presign(method: str, key: str, expires: int = 3600) -> str | None:
    """يولّد رابطاً موقّعاً (presigned URL) لعملية (PUT/GET/DELETE) على كائن في B2.
    التوقيع على ترويسة host فقط — العميل يقدر يبعت Content-Type (يُخزَّن كما هو) بدون كسر التوقيع."""
    if not is_configured():
        return None

    region = _region()
    host = _host()
    # .strip() يحمي من أي مسافات/أسطر زيادة وقت لصق المفاتيح في Vercel
    bucket = (settings.b2_bucket or "").strip()
    access_key = (settings.b2_key_id or "").strip()
    secret_key = (settings.b2_app_key or "").strip()

    now = datetime.now(timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")

    canonical_uri = "/" + _uri_encode(bucket, encode_slash=False) + "/" + _uri_encode(key, encode_slash=False)
    credential_scope = f"{datestamp}/{region}/{_SERVICE}/aws4_request"

    query = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": f"{access_key}/{credential_scope}",
        "X-Amz-Date": amzdate,
        "X-Amz-Expires": str(expires),
        "X-Amz-SignedHeaders": "host",
    }
    canonical_querystring = "&".join(
        f"{_uri_encode(k)}={_uri_encode(v)}" for k, v in sorted(query.items())
    )
    canonical_headers = f"host:{host}\n"
    signed_headers = "host"
    canonical_request = "\n".join([
        method.upper(),
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        "UNSIGNED-PAYLOAD",
    ])
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256",
        amzdate,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])
    signature = hmac.new(
        _signing_key(secret_key, datestamp, region),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"https://{host}{canonical_uri}?{canonical_querystring}&X-Amz-Signature={signature}"


def presign_put(key: str, expires: int = 3600) -> str | None:
    """رابط موقّع لرفع ملف (PUT) — صالح لمدة ساعة افتراضياً."""
    return presign("PUT", key, expires)


def presign_get(key: str, expires: int = 86400) -> str | None:
    """رابط موقّع لتحميل ملف (GET) — صالح 24 ساعة افتراضياً، ويُجدَّد في كل مرة تُعرض القائمة."""
    return presign("GET", key, expires)


def attach_download_urls(books: list, key_field: str = "file_path", url_field: str = "file_url") -> list:
    """يولّد رابط تحميل موقّع لكل كتاب له ملف مخزّن في B2 (يُجدَّد في كل طلب).
    لو B2 غير مضبوط، يترك القيم كما هي (روابط Supabase العامة القديمة)."""
    if not is_configured():
        return books
    for b in books:
        try:
            k = b.get(key_field)
            # نولّد رابط B2 فقط للكتب اللي مالهاش رابط محفوظ (كتب B2 بتُخزَّن بدون file_url).
            # كتب Supabase القديمة لها file_url عام محفوظ — نسيبه زي ما هو حتى لا تتكسر.
            if k and not b.get(url_field):
                url = presign_get(k)
                if url:
                    b[url_field] = url
        except Exception as e:
            logger.warning(f"attach_download_urls failed for one book: {e}")
    return books


def delete_object(key: str) -> bool:
    """حذف كائن من B2 عبر طلب DELETE موقّع."""
    url = presign("DELETE", key, 300)
    if not url:
        return False
    try:
        import httpx
        r = httpx.delete(url, timeout=30)
        ok = r.status_code in (200, 204)
        if not ok:
            logger.warning(f"B2 delete returned {r.status_code}: {r.text[:200]}")
        return ok
    except Exception as e:
        logger.warning(f"B2 delete failed: {e}")
        return False
