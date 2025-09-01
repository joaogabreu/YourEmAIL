from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import text

from extensions import db
from routes.storage import storage_bp, save_classification, _user_key
from services import gemini, gmail
from config.settings import CORS_ALLOWED_ORIGINS, DATABASE_URL, DEBUG, PORT

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def _init_database(retries: int = 15, delay: float = 2.0) -> None:
    import time
    from models import ClassificationRecord, UserGuidelines  # noqa: F401

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
            return
        except Exception as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(delay)
    if last_error:
        print(f"[warn] Banco indisponível no startup: {last_error}")

_init_database()

if CORS_ALLOWED_ORIGINS == "*":
    CORS(app, resources={r"/api/*": {"origins": "*"}})
else:
    CORS(app, resources={r"/api/*": {"origins": CORS_ALLOWED_ORIGINS}})

app.register_blueprint(storage_bp)

@app.route('/')
def health_check():
    """Health check endpoint para serviços de deploy."""
    db_status = "ok"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {exc}"
    return jsonify({
        'status': 'ok',
        'message': 'Email Classifier API is running',
        'database': db_status,
    })

@app.route('/api/classify', methods=['POST'])
def classify_email():
    data = request.get_json(force=True, silent=True) or {}
    email_content = data.get('email_content')
    subject = data.get('subject')
    guidelines = data.get('guidelines')
    if not email_content:
        return jsonify({'error': 'Missing email_content'}), 400

    try:
        cls = gemini.classify_email(email_content, subject, guidelines)
        result = gemini.generate_response(cls, email_content, subject)
        if 'classification' not in result:
            result = { **result, 'classification': cls }
        try:
            save_classification(
                _user_key(),
                cls,
                gmail_message_id=data.get('gmail_message_id'),
                subject=subject,
            )
        except Exception:
            pass
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401
    access_token = auth_header.split(' ')[1]

    try:
        max_results = int(request.args.get('maxResults', '20'))
        page_token = request.args.get('pageToken')
        data = gmail.get_emails(access_token, max_results, page_token)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/<message_id>/label', methods=['POST'])
def add_label(message_id: str):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401
    access_token = auth_header.split(' ')[1]

    data = request.get_json(force=True, silent=True) or {}
    label = data.get('label')
    if not label:
        return jsonify({'error': 'Missing label'}), 400
    try:
        gmail.add_label(access_token, message_id, label)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/classify-only', methods=['POST'])
def classify_only():
    """Classifica como 'Produtivo' ou 'Improdutivo' sem gerar resposta completa."""
    data = request.get_json(force=True, silent=True) or {}
    content = data.get('email_content')
    subject = data.get('subject')
    guidelines = data.get('guidelines')
    if not content:
        return jsonify({'error': 'Missing email_content'}), 400
    try:
        cls = gemini.classify_email(content, subject, guidelines)
        try:
            save_classification(
                _user_key(),
                cls,
                gmail_message_id=data.get('gmail_message_id'),
                subject=subject,
            )
        except Exception:
            pass
        return jsonify({'classification': cls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-reply', methods=['POST'])
def generate_reply():
    """Gera sugestão de resposta sob demanda para um e-mail já classificado."""
    data = request.get_json(force=True, silent=True) or {}
    classification = data.get('classification')
    content = data.get('email_content')
    subject = data.get('subject')
    if not classification or not content:
        return jsonify({'error': 'Missing classification or email_content'}), 400
    try:
        result = gemini.generate_response(classification, content, subject)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/classify-batch', methods=['POST'])
def classify_batch():
    """Classifica em lote uma lista de e-mails (somente Produtivo/Improdutivo),
    retornando um mapa {id: classification}. Não gera corpo de resposta.
    """
    data = request.get_json(force=True, silent=True) or {}
    emails = data.get('emails') or []
    guidelines = data.get('guidelines')
    if not isinstance(emails, list):
        return jsonify({'error': 'Invalid payload: emails must be a list'}), 400
    user_key = _user_key()
    try:
        result = {}
        for item in emails:
            try:
                content = (item or {}).get('body') or (item or {}).get('content') or ''
                subject = (item or {}).get('subject')
                msg_id = (item or {}).get('id')
                if not msg_id or not content:
                    continue
                cls = gemini.classify_email(content, subject, guidelines)
                result[msg_id] = cls
                try:
                    save_classification(
                        user_key,
                        cls,
                        gmail_message_id=msg_id,
                        subject=subject,
                    )
                except Exception:
                    pass
            except Exception:
                continue
        return jsonify({'classifications': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', PORT))
    app.run(debug=DEBUG, host='0.0.0.0', port=port)
