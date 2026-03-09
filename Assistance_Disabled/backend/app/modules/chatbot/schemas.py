from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatRequest(BaseModel):
    message: str
    language: str = "en"        # en, hi, te
    session_id: int = None      # optional - continue existing session


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    session_id: int
    user_message: str
    assistant_reply: str


class SessionHistoryResponse(BaseModel):
    session_id: int
    messages: List[MessageResponse]

    class Config:
        from_attributes = True