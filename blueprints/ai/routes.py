import os
from flask import render_template, request, jsonify, session, current_app, redirect, url_for
from extensions import db
from models.document import Document
from models.course import Course
from models.user_ai_config import UserAIConfig
from services.document_parser import process_uploaded_document
from services.ai_service import ask_study_assistant, SUPPORTED_MODELS, resolve_api_keys
from utils.auth import login_required
from blueprints.ai import ai_bp

@ai_bp.route('/study-assistant')
@login_required
def study_assistant_page():
    user_id = session['user_id']
    documents = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).all()
    courses = Course.query.filter_by(user_id=user_id).all()
    
    secret_key = current_app.config.get('SECRET_KEY', 'fyp_secret_key_2026')
    config = UserAIConfig.query.filter_by(user_id=user_id).first()
    config_dict = config.to_dict(secret_key) if config else {
        "has_google_key": False,
        "google_key_masked": "",
        "has_openrouter_key": False,
        "openrouter_key_masked": "",
        "default_provider": "google",
        "default_model": "gemini-2.0-flash"
    }

    # Check if system fallback keys exist
    env_keys = resolve_api_keys(user_id)
    config_dict["is_fallback_google"] = env_keys["is_fallback_google"]
    config_dict["is_fallback_openrouter"] = env_keys["is_fallback_openrouter"]

    return render_template(
        'study_assistant.html',
        active_page='study_assistant',
        documents=documents,
        courses=courses,
        ai_config=config_dict,
        supported_models=SUPPORTED_MODELS
    )

@ai_bp.route('/api/ai/upload-document', methods=['POST'])
@login_required
def upload_document():
    user_id = session['user_id']
    file = request.files.get('file')
    if not file:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400

    course_id = request.form.get('course_id')
    if course_id in ['', 'none', 'null']:
        course_id = None

    try:
        parsed_meta = process_uploaded_document(file, user_id)
        
        doc = Document(
            user_id=user_id,
            course_id=course_id,
            filename=parsed_meta["filename"],
            file_path=parsed_meta["file_path"],
            file_type=parsed_meta["file_type"],
            file_size=parsed_meta["file_size"],
            extracted_text=parsed_meta["extracted_text"],
            summary=parsed_meta["summary"]
        )
        db.session.add(doc)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Successfully uploaded and parsed '{doc.filename}'!",
            "document": doc.to_dict()
        })
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error saving document: {str(e)}"}), 500

@ai_bp.route('/api/ai/documents/<string:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    if not doc:
        return jsonify({"status": "error", "message": "Document not found."}), 404

    # Remove physical file from disk
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    db.session.delete(doc)
    db.session.commit()
    return jsonify({"status": "success", "message": "Document deleted successfully."})

@ai_bp.route('/api/ai/documents/<string:doc_id>/preview')
@login_required
def preview_document(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    if not doc:
        return jsonify({"status": "error", "message": "Document not found."}), 404
    return jsonify({"status": "success", "document": doc.to_dict(include_text=True)})

@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def chat():
    user_id = session['user_id']
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({"status": "error", "message": "Please enter a question or prompt."}), 400

    selected_doc_ids = data.get('selected_doc_ids', [])
    provider = data.get('provider')
    model = data.get('model')

    try:
        result = ask_study_assistant(
            user_id=user_id,
            prompt=prompt,
            selected_doc_ids=selected_doc_ids,
            provider_override=provider,
            model_override=model
        )
        return jsonify({"status": "success", "data": result})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Unexpected AI error: {str(e)}"}), 500

@ai_bp.route('/api/ai/config', methods=['GET', 'POST'])
@login_required
def ai_config():
    user_id = session['user_id']
    secret_key = current_app.config.get('SECRET_KEY', 'fyp_secret_key_2026')
    config = UserAIConfig.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        if not config:
            config = UserAIConfig(user_id=user_id)
            db.session.add(config)

        if 'google_api_key' in data and data['google_api_key'].strip():
            config.set_google_key(data['google_api_key'].strip(), secret_key)
        elif data.get('clear_google_key'):
            config.google_api_key_encrypted = None

        if 'openrouter_api_key' in data and data['openrouter_api_key'].strip():
            config.set_openrouter_key(data['openrouter_api_key'].strip(), secret_key)
        elif data.get('clear_openrouter_key'):
            config.openrouter_api_key_encrypted = None

        if 'default_provider' in data:
            prov = data['default_provider'].strip().lower()
            if prov in ['google', 'openrouter']:
                config.default_provider = prov

        if 'default_model' in data and data['default_model'].strip():
            config.default_model = data['default_model'].strip()

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "AI configuration saved securely!",
            "config": config.to_dict(secret_key)
        })

    # GET
    res = config.to_dict(secret_key) if config else {
        "has_google_key": False,
        "google_key_masked": "",
        "has_openrouter_key": False,
        "openrouter_key_masked": "",
        "default_provider": "google",
        "default_model": "gemini-2.0-flash"
    }
    return jsonify(res)
