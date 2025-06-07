from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from typing import Optional, Literal
import modal
import asyncio

router = APIRouter()
chat_histories = {}

# Supported languages with type safety
SupportedLanguage = Literal["yoruba", "igbo", "hausa", "swahili", "english"]


class ChatRequest(BaseModel):
    message: str
    language: SupportedLanguage = "english"
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


class HistoryResponse(BaseModel):
    history: list


@router.post("/ai-companion/chat", response_model=ChatResponse)
async def chat_with_ai(
        request: Request,
        payload: ChatRequest
):
    try:
        # Get the Modal app from FastAPI state
        modal_app = request.app.state.modal_app

        # Run the Modal function asynchronously
        loop = asyncio.get_event_loop()
        ai_reply = await loop.run_in_executor(
            None,
            lambda: modal_app.run_mistral.remote(payload.message, payload.language)
        )

        # Store in history if user_id provided
        if payload.user_id:
            chat_histories.setdefault(payload.user_id, []).append({
                "question": payload.message,
                "answer": ai_reply,
                "language": payload.language
            })

        return {"response": ai_reply}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

@router.get("/ai-companion/history", response_model=HistoryResponse)
async def get_chat_history(
    user_id: str = Query(..., description="User ID to fetch history for")
):
    history = chat_histories.get(user_id, [])
    return {"history": history}

@router.delete("/ai-companion/history", status_code=204)
async def clear_chat_history(
    user_id: str = Query(..., description="User ID to clear history for")
):
    chat_histories.pop(user_id, None)
    return