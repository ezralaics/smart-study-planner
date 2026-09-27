---
name: ai-service-integration
description: Use this skill when implementing, refactoring, or testing LLM chatbot features, document parsing (PDF/TXT/Images), Google Gemini API, OpenRouter API, or Bring Your Own Key (BYOK) encryption.
---

# AI Service & Knowledge Base Integration Skill

This skill outlines the standards for integrating multi-provider AI features in the Smart Study Planner.

## 1. Provider Adapter Pattern
When dispatching prompts to LLMs, use a unified interface in `services/ai_service.py`:

```python
class AIServiceAdapter:
    @staticmethod
    def generate_response(provider: str, model: str, api_key: str, system_prompt: str, user_prompt: str, context: str = "") -> str:
        if provider == "google":
            # Call Google GenAI SDK (gemini-1.5-flash / gemini-2.0-flash)
            ...
        elif provider == "openrouter":
            # Call OpenRouter API (https://openrouter.ai/api/v1/chat/completions)
            ...
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
```

## 2. Document Extraction Protocols
- **PDF Files:** Extract text using `pypdf.PdfReader`. Truncate or chunk if token length exceeds model limits.
- **Images:** Pass directly to Gemini's multimodal vision API or extract text using OCR.
- **Text Files:** Read with UTF-8 decoding and fallback to Latin-1 on decode failure.

## 3. Key Encryption & Security
- Encrypt API keys before database storage using `cryptography.fernet.Fernet`.
- Mask keys in UI responses: `f"{key[:6]}••••••••{key[-4:]}"`.

## 4. Verification Checklist
1. Test with an invalid API key -> verify a clean HTTP 400 JSON response with user-friendly error message.
2. Test upload with non-permitted file type (e.g. `.exe`) -> verify rejection.
3. Test prompt generation with mock LLM response in `test_suite.py`.
