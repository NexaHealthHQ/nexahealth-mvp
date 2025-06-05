import requests
import os
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
MODEL = "google/gemini-2.0-flash-exp:free"

def detect_language(text: str) -> str:
    # Simple keyword-based detection (expand as needed)
    yoruba_keywords = ["bawo", "se", "ni", "owo", "ire"]
    pidgin_keywords = ["how far", "abi", "no be", "wahala", "dem"]
    hausa_keywords = ["sannu", "lafiya", "yaya", "nagode", "ina"]

    text_lower = text.lower()

    if any(re.search(rf"\b{word}\b", text_lower) for word in yoruba_keywords):
        return "Yoruba"
    elif any(re.search(rf"\b{word}\b", text_lower) for word in pidgin_keywords):
        return "Pidgin English"
    elif any(re.search(rf"\b{word}\b", text_lower) for word in hausa_keywords):
        return "Hausa"
    else:
        return "English"

def get_ai_response(message: str, history=None) -> str:
    if history is None:
        history = []

    user_language = detect_language(message)

    # Compose system prompt with language info
    system_prompt = (
        f"You are Nexa AI Health Companion, a friendly and empathetic health assistant designed for Africans. "
        f"Speak clearly and kindly in simple language, including African local languages like Yoruba, Pidgin, Hausa, and Swahili when appropriate. "
        f"Detected user language: {user_language}. "
        "Provide short, easy-to-understand advice about symptoms and mental health without overwhelming the user. "
        "Do not make any medical diagnoses, but offer helpful suggestions, ask clarifying questions gently, and encourage users to seek professional help when needed. "
        "Always keep your tone supportive and culturally sensitive."
    )

    # Build messages with history + current message
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    return response.json()["choices"][0]["message"]["content"]
