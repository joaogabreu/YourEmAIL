from datetime import datetime, timezone

from extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserGuidelines(db.Model):
    __tablename__ = "user_guidelines"

    user_key = db.Column(db.String(128), primary_key=True)
    produtivo_text = db.Column(db.Text, nullable=False, default="")
    improdutivo_text = db.Column(db.Text, nullable=False, default="")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    def to_dict(self) -> dict:
        return {
            "user_key": self.user_key,
            "produtivo_text": self.produtivo_text,
            "improdutivo_text": self.improdutivo_text,
            "guidelines": self.as_guidelines_string(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def as_guidelines_string(self) -> str:
        if not self.produtivo_text and not self.improdutivo_text:
            return ""
        return f"Produtivo: {self.produtivo_text}. Improdutivo: {self.improdutivo_text}."


class ClassificationRecord(db.Model):
    __tablename__ = "classification_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_key = db.Column(db.String(128), nullable=False, index=True)
    gmail_message_id = db.Column(db.String(128), nullable=True, index=True)
    subject = db.Column(db.String(512), nullable=True)
    classification = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_key": self.user_key,
            "gmail_message_id": self.gmail_message_id,
            "subject": self.subject,
            "classification": self.classification,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
