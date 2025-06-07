from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import verify, report, map, risk, nearby, ai_companion, feedback
import modal  # Add this import

app = FastAPI(title="NexaHealth API")

# Initialize Modal client
app.state.modal_app = modal.App.lookup("nexahealth-mistral")  # Must match your deployed app name

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342", "https://nexahealth.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(verify.router)
app.include_router(report.router)
app.include_router(map.router)
app.include_router(risk.router)
app.include_router(nearby.router)
app.include_router(ai_companion.router)
app.include_router(feedback.router)

@app.get("/")
async def root():
    return {"message": "NexaHealth"}