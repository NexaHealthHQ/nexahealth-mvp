import requests
import os
import re
from typing import Optional, List, Dict

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.0-flash-exp:free"

# Language configuration with structured templates
LANGUAGE_TEMPLATES = {
    "english": {
        "greeting": "Hello! 👋",
        "sections": [
            ("Understanding Your Concern", "🔍"),
            ("Recommended Actions", "🩺"),
            ("When to Seek Help", "⚠️"),
            ("Follow-up", "💬")
        ],
        "closing": "Would you like me to clarify anything?"
    },
    "pidgin": {
        "greeting": "How far! 👋",
        "sections": [
            ("Wetin I Sabi", "🔍"),
            ("Wetin You Fit Do", "🩺"),
            ("When to See Doctor", "⚠️"),
            ("Make We Talk More", "💬")
        ],
        "closing": "You get any question?"
    },
    "yoruba": {
        "greeting": "Bawo ni! 👋",
        "sections": [
            ("Ohun ti Mo Gbọ", "🔍"),
            ("Ohun ti O Le Ṣe", "🩺"),
            ("Igba ti O Yẹ Lati Raa Dokita", "⚠️"),
            ("Atunṣe", "💬")
        ],
        "closing": "Ṣe o ni ibeere miiran?"
    },
    "hausa": {
        "greeting": "Sannu! 👋",
        "sections": [
            ("Abin da Na Gane", "🔍"),
            ("Abin da Zaka iya Yi", "🩺"),
            ("Lokacin Neman Taimako", "⚠️"),
            ("Ci gaba", "💬")
        ],
        "closing": "Kuna da wani tambaya?"
    }
}


def detect_language(text: str) -> str:
    """Improved language detection with confidence scoring"""
    language_keywords = {
        "pidgin": [r"\bhow far\b", r"\babi\b", r"\bno be\b", r"\bwahala\b"],
        "yoruba": [r"\bbawo\b", r"\bse\b", r"\bni\b", r"\bowo\b"],
        "hausa": [r"\bsannu\b", r"\blafiya\b", r"\byaya\b", r"\bnagode\b"]
    }

    text_lower = text.lower()
    scores = {lang: sum(bool(re.search(p, text_lower)) for p in patterns)
              for lang, patterns in language_keywords.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "english"


def structure_response(raw_response: str, language: str) -> str:
    """
    Transforms raw AI response into a beautifully formatted message with:
    - Clear section headers
    - Proper line breaks
    - Emoji visual cues
    - Consistent structure
    """
    template = LANGUAGE_TEMPLATES.get(language, LANGUAGE_TEMPLATES["english"])

    # Split response into logical parts
    parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', raw_response) if p.strip()]

    # Build structured response
    lines = [f"**Nexa Health Companion**\n{template['greeting']}\n"]

    # Add sections with appropriate content
    for i, (section, emoji) in enumerate(template["sections"]):
        if i < len(parts):
            lines.append(f"\n**{emoji} {section}**\n{parts[i]}\n")

    # Add closing prompt
    lines.append(f"\n{template['closing']}")

    return "\n".join(lines)


def get_ai_response(message: str, history: Optional[List[Dict]] = None) -> str:
    """Gets formatted AI response with proper structure"""
    if history is None:
        history = []

    language = detect_language(message)

    system_prompt = f"""You are Nexa, a friendly African health assistant. Respond in {language} when appropriate.

    Structure your responses clearly:
    1. Briefly acknowledge the concern
    2. Provide 2-3 practical suggestions 
    3. Mention warning signs
    4. End with an open question

    Keep responses:
    - Under 4 sentences per section
    - Culturally appropriate
    - Professional yet warm"""

    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": message}
    ]

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
                "temperature": 0.7,
                "max_tokens": 300  # Limit response length
            },
            timeout=10
        )
        response.raise_for_status()

        raw_content = response.json()["choices"][0]["message"]["content"]
        return structure_response(raw_content, language)

    except Exception as e:
        return "**Nexa Health Companion**\n\nSorry, I'm experiencing technical difficulties. Please try again later. 🛠️"