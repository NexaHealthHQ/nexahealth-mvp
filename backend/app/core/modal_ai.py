from typing import Optional, Literal
from pydantic import BaseModel
import requests
import os

SUPPORTED_LANGUAGES = {
    "yoruba": "Yoruba",
    "igbo": "Igbo",
    "hausa": "Hausa",
    "swahili": "Swahili",
    "english": "English"
}


class HealthQuery(BaseModel):
    question: str
    language: Literal["yoruba", "igbo", "hausa", "swahili", "english"] = "english"


def query_mistral(query: HealthQuery) -> str:
    """Call Modal-hosted Mistral 7B API"""
    MODAL_URL = os.getenv(
        "MODAL_URL",
        "https://Justreading--nexahealth-mistral.modal.run/answer_question"
    )

    try:
        response = requests.post(
            MODAL_URL,
            json={
                "question": query.question,
                "language": query.language
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("answer", "I couldn't generate a response.")

    except requests.exceptions.RequestException as e:
        error_msg = f"AI service error: {str(e)}"
        lang_name = SUPPORTED_LANGUAGES.get(query.language, "English")
        return f"({lang_name}) Sorry, I'm having trouble responding right now. Please try again later."