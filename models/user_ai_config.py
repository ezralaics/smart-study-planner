import uuid
import base64
import hashlib
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from extensions import db, GUID

def get_fernet(secret_key: str) -> Fernet:
    """Derives a deterministic 32-byte URL-safe base64 Fernet key from secret_key."""
    key_bytes = hashlib.sha256(secret_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

def encrypt_value(value: str, secret_key: str) -> str:
    if not value or not value.strip():
        return ""
    f = get_fernet(secret_key)
    return f.encrypt(value.strip().encode('utf-8')).decode('utf-8')

def decrypt_value(encrypted: str, secret_key: str) -> str:
    if not encrypted or not encrypted.strip():
        return ""
    try:
        f = get_fernet(secret_key)
        return f.decrypt(encrypted.strip().encode('utf-8')).decode('utf-8')
    except Exception:
        return ""

def mask_value(raw: str) -> str:
    if not raw or not raw.strip():
        return ""
    s = raw.strip()
    if len(s) <= 8:
        return "••••••••"
    return s[:4] + "••••••••" + s[-4:]


class UserAIConfig(db.Model):
    __tablename__ = 'user_ai_configs'

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)

    google_api_key_encrypted = db.Column(db.Text, nullable=True)
    openrouter_api_key_encrypted = db.Column(db.Text, nullable=True)
    default_provider = db.Column(db.String(30), default='google', nullable=False)
    default_model = db.Column(db.String(80), default='gemini-2.0-flash', nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship('User', backref=db.backref('ai_config', uselist=False, cascade='all, delete-orphan'))

    def set_google_key(self, raw_key: str, secret_key: str):
        self.google_api_key_encrypted = encrypt_value(raw_key, secret_key) if raw_key else None

    def get_google_key(self, secret_key: str) -> str:
        return decrypt_value(self.google_api_key_encrypted, secret_key)

    def set_openrouter_key(self, raw_key: str, secret_key: str):
        self.openrouter_api_key_encrypted = encrypt_value(raw_key, secret_key) if raw_key else None

    def get_openrouter_key(self, secret_key: str) -> str:
        return decrypt_value(self.openrouter_api_key_encrypted, secret_key)

    def to_dict(self, secret_key: str):
        raw_google = self.get_google_key(secret_key)
        raw_or = self.get_openrouter_key(secret_key)
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "has_google_key": bool(raw_google),
            "google_key_masked": mask_value(raw_google),
            "has_openrouter_key": bool(raw_or),
            "openrouter_key_masked": mask_value(raw_or),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
