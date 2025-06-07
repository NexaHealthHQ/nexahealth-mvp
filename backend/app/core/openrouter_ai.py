import requests
import os
import re
from typing import Optional

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
MODEL = "google/gemini-2.0-flash-exp:free"


def detect_language(text: str) -> str:
    """Detect language based on keywords with improved matching"""
    language_patterns = {
        "Yoruba": [r"\bbawo\b", r"\bse\b", r"\bni\b", r"\bowo\b", r"\bire\b"],
        "Pidgin English": [r"\bhow far\b", r"\babi\b", r"\bno be\b", r"\bwahala\b", r"\bdem\b"],
        "Hausa": [r"\bsannu\b", r"\blafiya\b", r"\byaya\b", r"\bnagode\b", r"\bina\b"]
    }

    text_lower = text.lower()
    for lang, patterns in language_patterns.items():
        if any(re.search(pattern, text_lower) for pattern in patterns):
            return lang
    return "English"


def enhance_response(raw_response: str, language: str) -> str:
    """
    Intelligently enhances the raw AI response with consistent formatting,
    emojis, and conversation prompts while preserving its original meaning.
    """
    # Language-specific configurations
    enhancements = {
        "Pidgin English": {
            "greeting": "Ah!",
            "advice_header": "**Wetin you fit do:**",
            "prompt": "**Abeg tell me:** How you dey feel now? You wan talk more? 🙏",
            "emojis": ["😊", "💧", "👍"]
        },
        "Yoruba": {
            "greeting": "E kaaro!",
            "advice_header": "**Ohun ti o le se:**",
            "prompt": "**Jowo so fun mi:** Se o ni nkan miiran ti o fe so? 💬",
            "emojis": ["🌟", "🚰", "🙌"]
        },
        "Hausa": {
            "greeting": "Sannu!",
            "advice_header": "**Abin da za ka iya yi:**",
            "prompt": "**Don Allah a gaya mani:** Kana jin kara magana? 📢",
            "emojis": ["🌞", "💦", "👌"]
        },
        "English": {
            "greeting": "Hello!",
            "advice_header": "**What you can do:**",
            "prompt": "",
            "emojis": ["👋", "💧", "✨"]
        }
    }

    config = enhancements.get(language, enhancements["English"])

    # Split response into sentences while preserving the original meaning
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_response) if s.strip()]

    # Build enhanced response
    enhanced = [f"**Nexa AI:**\n\n{config['greeting']} {sentences[0]}{config['emojis'][0]}\n\n"]

    if len(sentences) > 1:
        enhanced.append(f"{config['advice_header']}\n")
        for sentence in sentences[1:]:
            enhanced.append(f"- {sentence}\n")
        enhanced.append(f"\n")

    # Always add hydration reminder and conversation prompt
    enhanced.append(f"- Remember to drink water {config['emojis'][1]}\n\n")
    enhanced.append(config['prompt'])

    return "".join(enhanced)


def get_ai_response(message: str, history: Optional[list] = None) -> str:
    """Get AI response with automatic language detection and enhanced formatting"""
    if history is None:
        history = []

    user_language = detect_language(message)

    # Enhanced system prompt that encourages structured responses
    system_prompt = (
        f"You are Nexa AI Health Companion, a friendly health assistant for Africans. "
        f"Respond in {user_language} when appropriate. Keep responses:\n"
        f"- Conversational but professional\n"
        f"- 2-3 short paragraphs maximum\n"
        f"- Include practical advice\n"
        f"- End with an open-ended question\n"
        f"Current conversation language: {user_language}\n"
        f"Important: Don't diagnose, just suggest and recommend professional help when needed."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7  # For more creative responses
            },
            timeout=10
        )
        response.raise_for_status()

        raw_response = response.json()["choices"][0]["message"]["content"]
        return enhance_response(raw_response, user_language)

    except requests.exceptions.RequestException as e:
        return f"**Nexa AI:**\n\nSorry, I'm having trouble responding right now. Please try again later. 🙏"