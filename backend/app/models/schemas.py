# نماذج البيانات - Morix Platform
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.config import settings


class LoginRequest(BaseModel):
    email: str
    password: str

    @classmethod
    def validate_email_domain(cls, v):
        if not v.lower().endswith(f"@{settings.allowed_email_domain}"):
            raise ValueError(f"الإيميل لازم يكون @{settings.allowed_email_domain}")
        return v.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class SchoolSetupRequest(BaseModel):
    school_id: str
    students: List[dict]
    teachers: List[dict]
    admins_count: int = 1


class GeneratedAccount(BaseModel):
    full_name: str
    email: str
    password: str
    role: str
    grade: Optional[str] = None
    subject: Optional[str] = None
    ministry_id: Optional[str] = None


class AccountsResponse(BaseModel):
    accounts: List[GeneratedAccount]
    total: int
    school_name: str


class DiagnosticAnswer(BaseModel):
    question_id: int
    answer: str


class DiagnosticSubmit(BaseModel):
    answers: List[DiagnosticAnswer]


class DiagnosticResult(BaseModel):
    learning_style: str
    visual_score: int
    auditory_score: int
    kinesthetic_score: int
    description: str


class ChatMessage(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    book_id: Optional[str] = None
    image_base64: Optional[str] = None   # base64 صورة مرفقة
    file_text: Optional[str] = None      # نص ملف مرفق (PDF/TXT)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    from_cache: bool = False


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    book_title: Optional[str] = None


class BookCreate(BaseModel):
    title: str
    subject: str
    grade: str
    raw_text: Optional[str] = None
    key_concepts: Optional[List[str]] = []


class BookResponse(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    summary: Optional[str]
    key_concepts: List[Any] = []
    is_active: bool


class StatsResponse(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_admins: int
    total_conversations: int
    learning_styles: dict
    recent_logins: int


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    brightness: Optional[int] = None
    difficulty: Optional[str] = None
    hobbies: Optional[List[str]] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None  # يُخزَّن في جدول users


class ComplaintCreate(BaseModel):
    type: str = "complaint"
    title: str
    content: str


class ImageGenerateRequest(BaseModel):
    prompt: str


class GameGenerateRequest(BaseModel):
    game_type: str
    subject: str
    topic: Optional[str] = ""
