from fastapi import APIRouter
from pydantic import BaseModel
from src.ai.chatbot import RealEstateChatbot

router = APIRouter(tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

_bot = None

def get_bot() -> RealEstateChatbot:
    global _bot
    if _bot is None:
        _bot = RealEstateChatbot()
    return _bot


@router.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    bot = get_bot()
    answer = bot.ask(request.message)
    return ChatResponse(answer=answer)


@router.post("/chat/reset/")
async def reset_chat():
    bot = get_bot()
    bot.reset()
    return {"status": "ok", "message": "Chat history cleared"}