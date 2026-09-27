import os
import requests
from flask import current_app
from extensions import db
from models.document import Document
from models.user_ai_config import UserAIConfig

ACADEMIC_SYSTEM_PERSONA = """You are an expert, encouraging university Academic Study Assistant and Tutor embedded in the Smart Study Planner application.
Your mission is to help students comprehend complex concepts, analyze their lecture slides and textbook excerpts, practice exam-style questions, and master difficult formulas.

Follow these strict pedagogical guidelines:
1. Ground your answers primarily in the student's uploaded notes provided in the context.
2. Cite the source document (e.g. [Source: Chapter 2 Notes]) when quoting or synthesizing facts from the material.
3. If the uploaded material does not contain the answer, explicitly state: "The uploaded notes do not specifically cover this topic, but here is a general academic explanation:" before proceeding.
4. Format mathematical expressions using standard LaTeX syntax (e.g. $E = mc^2$ or $$\\int_a^b f(x)dx$$).
5. Use organized structure: bold headings, clean bullet points, and code blocks for programming snippets.
"""

# Supported model directories
SUPPORTED_MODELS = {
    "google": [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash (Fast & Free)", "badge": "Recommended"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "badge": "High Context"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "badge": "Complex Reasoning"}
    ],
    "openrouter": [
        {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1 (Reasoning)", "badge": "High IQ"},
        {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "badge": "Elite Writing"},
        {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B", "badge": "Open Weights"},
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "badge": "Balanced"}
    ]
}

def resolve_api_keys(user_id: str) -> dict:
    """
    Retrieves user decrypted keys with fallback to system environment variables.
    """
    secret_key = current_app.config.get('SECRET_KEY', 'fyp_secret_key_2026')
    config = UserAIConfig.query.filter_by(user_id=user_id).first()

    google_key = ""
    openrouter_key = ""
    default_provider = "google"
    default_model = "gemini-2.0-flash"

    if config:
        google_key = config.get_google_key(secret_key)
        openrouter_key = config.get_openrouter_key(secret_key)
        default_provider = config.default_provider or "google"
        default_model = config.default_model or "gemini-2.0-flash"

    # Fallback to system env if user hasn't provided their own (convenience for demo/recruiter accounts)
    is_fallback_google = False
    is_fallback_openrouter = False

    if not google_key:
        env_google = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY') or current_app.config.get('GOOGLE_API_KEY')
        if env_google and env_google.strip():
            google_key = env_google.strip()
            is_fallback_google = True

    if not openrouter_key:
        env_or = os.environ.get('OPENROUTER_API_KEY') or current_app.config.get('OPENROUTER_API_KEY')
        if env_or and env_or.strip():
            openrouter_key = env_or.strip()
            is_fallback_openrouter = True

    return {
        "google_key": google_key,
        "is_fallback_google": is_fallback_google,
        "openrouter_key": openrouter_key,
        "is_fallback_openrouter": is_fallback_openrouter,
        "default_provider": default_provider,
        "default_model": default_model
    }

def build_context_prompt(user_prompt: str, documents: list) -> str:
    """Constructs prompt containing selected academic documents as grounded context."""
    if not documents:
        return user_prompt

    context_sections = []
    total_chars = 0
    max_context_chars = 40000  # Cap context budget safely for fast response

    for doc in documents:
        if not doc.extracted_text:
            continue
        course_name = doc.course.course_name if doc.course else "General"
        header = f"=== DOCUMENT: {doc.filename} (Subject: {course_name}) ==="
        body = doc.extracted_text.strip()
        
        # Avoid overflowing token limits
        if total_chars + len(body) > max_context_chars:
            remaining = max(0, max_context_chars - total_chars)
            body = body[:remaining] + "\n[... Document truncated due to context limits ...]"
        
        context_sections.append(f"{header}\n{body}\n=== END DOCUMENT ===")
        total_chars += len(body)
        if total_chars >= max_context_chars:
            break

    if not context_sections:
        return user_prompt

    full_context = "\n\n".join(context_sections)
    return (
        f"STUDY DOCUMENTS CONTEXT:\n"
        f"{full_context}\n\n"
        f"========================================\n"
        f"STUDENT'S INQUIRY:\n"
        f"{user_prompt}\n"
        f"========================================\n"
        f"Please provide an accurate, grounded, and pedagogical response following your academic tutoring guidelines."
    )

def query_google_gemini(api_key: str, model: str, prompt: str) -> str:
    """Invokes Google Gemini REST API."""
    if not api_key:
        raise ValueError("Google Gemini API key is missing. Please add your key in the AI Settings modal (get a free key at https://aistudio.google.com).")

    # Map model aliases if necessary
    model_name = model or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": ACADEMIC_SYSTEM_PERSONA}]
        },
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2500
        }
    }

    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
        data = res.json()

        if res.status_code != 200:
            error_msg = data.get('error', {}).get('message', res.text)
            if 'API_KEY_INVALID' in str(error_msg) or res.status_code == 400:
                raise ValueError("Google Gemini API key is invalid or unauthorized. Please verify your key from Google AI Studio.")
            elif res.status_code == 429:
                raise ValueError("Google Gemini rate limit exceeded. Please wait a moment and try again.")
            raise ValueError(f"Google Gemini Error: {error_msg}")

        candidates = data.get('candidates', [])
        if not candidates:
            return "Gemini did not return an answer (content might have triggered safety filters)."

        parts = candidates[0].get('content', {}).get('parts', [])
        if not parts:
            return "No text returned by the model."

        return parts[0].get('text', '').strip()

    except requests.exceptions.Timeout:
        raise ValueError("Google Gemini request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error connecting to Google Gemini: {str(e)}")

def query_openrouter(api_key: str, model: str, prompt: str) -> str:
    """Invokes OpenRouter chat completions REST API."""
    if not api_key:
        raise ValueError("OpenRouter API key is missing. Please add your key in the AI Settings modal (get one at https://openrouter.ai).")

    model_name = model or "deepseek/deepseek-r1"
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://laikwangzhe.com",
        "X-Title": "Smart Study Planner",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": ACADEMIC_SYSTEM_PERSONA},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=50)
        data = res.json()

        if res.status_code != 200:
            error_info = data.get('error', {})
            error_msg = error_info.get('message', res.text)
            if res.status_code == 401:
                raise ValueError("OpenRouter API key is invalid. Please check your key at https://openrouter.ai/keys.")
            elif res.status_code == 402:
                raise ValueError("OpenRouter insufficient account credits. Please check your OpenRouter balance.")
            elif res.status_code == 429:
                raise ValueError("OpenRouter model rate limit exceeded. Please retry in a few seconds.")
            raise ValueError(f"OpenRouter Error: {error_msg}")

        choices = data.get('choices', [])
        if not choices:
            return "OpenRouter returned an empty response."

        message = choices[0].get('message', {})
        return message.get('content', '').strip()

    except requests.exceptions.Timeout:
        raise ValueError("OpenRouter request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error connecting to OpenRouter: {str(e)}")

def ask_study_assistant(user_id: str, prompt: str, selected_doc_ids: list = None,
                         provider_override: str = None, model_override: str = None) -> dict:
    """
    Main entry point: Resolves keys, collects active documents, invokes selected model,
    and returns formatted answer with citation metadata.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Please provide a question or topic for the Study Assistant.")

    keys_info = resolve_api_keys(user_id)

    # Determine provider and model
    provider = (provider_override or keys_info['default_provider'] or 'google').lower()
    if provider not in ['google', 'openrouter']:
        provider = 'google'

    model = model_override
    if not model:
        model = keys_info['default_model']
        if provider == 'google' and ('gemini' not in model):
            model = 'gemini-2.0-flash'
        elif provider == 'openrouter' and ('gemini' in model):
            model = 'deepseek/deepseek-r1'

    # Retrieve selected documents
    docs = []
    if selected_doc_ids:
        docs = Document.query.filter(
            Document.user_id == user_id,
            Document.id.in_(selected_doc_ids)
        ).all()

    assembled_prompt = build_context_prompt(prompt.strip(), docs)

    # Execute inference
    if provider == 'google':
        answer = query_google_gemini(keys_info['google_key'], model, assembled_prompt)
    else:
        answer = query_openrouter(keys_info['openrouter_key'], model, assembled_prompt)

    cited_docs = [d.filename for d in docs]

    return {
        "answer": answer,
        "provider": provider,
        "model": model,
        "documents_considered": len(docs),
        "cited_documents": cited_docs
    }
