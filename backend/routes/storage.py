from flask import Blueprint, jsonify, request

from extensions import db
from models import ClassificationRecord, UserGuidelines

storage_bp = Blueprint("storage", __name__)

DEFAULT_USER_KEY = "default"


def _user_key() -> str:
    return (request.headers.get("X-User-Key") or DEFAULT_USER_KEY).strip()[:128] or DEFAULT_USER_KEY


@storage_bp.route("/api/guidelines", methods=["GET"])
def get_guidelines():
    row = db.session.get(UserGuidelines, _user_key())
    if not row:
        return jsonify({
            "user_key": _user_key(),
            "produtivo_text": "",
            "improdutivo_text": "",
            "guidelines": "",
        })
    return jsonify(row.to_dict())


@storage_bp.route("/api/guidelines", methods=["PUT"])
def put_guidelines():
    data = request.get_json(force=True, silent=True) or {}
    produtivo = (data.get("produtivo_text") or "").strip()
    improdutivo = (data.get("improdutivo_text") or "").strip()
    key = _user_key()

    row = db.session.get(UserGuidelines, key)
    if not row:
        row = UserGuidelines(user_key=key)
        db.session.add(row)

    row.produtivo_text = produtivo
    row.improdutivo_text = improdutivo
    db.session.commit()
    return jsonify(row.to_dict())


@storage_bp.route("/api/history", methods=["GET"])
def get_history():
    raw_limit = request.args.get("limit", "50")
    try:
        limit = int(raw_limit)
    except ValueError:
        return jsonify({"error": "Invalid limit: must be an integer"}), 400
    if limit < 1:
        return jsonify({"error": "Invalid limit: must be at least 1"}), 400
    limit = min(limit, 200)
    rows = (
        ClassificationRecord.query
        .filter_by(user_key=_user_key())
        .order_by(ClassificationRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify({"items": [r.to_dict() for r in rows]})


def save_classification(
    user_key: str,
    classification: str,
    *,
    gmail_message_id: str | None = None,
    subject: str | None = None,
) -> None:
    row = ClassificationRecord(
        user_key=user_key,
        gmail_message_id=gmail_message_id,
        subject=(subject or "")[:512] or None,
        classification=classification,
    )
    db.session.add(row)
    db.session.commit()
