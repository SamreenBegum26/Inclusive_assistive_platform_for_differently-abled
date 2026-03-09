from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.chatbot.models import ChatSession, ChatMessage
from app.modules.chatbot.schemas import (
    ChatRequest,
    ChatResponse,
    SessionHistoryResponse
)
from app.modules.chatbot.service import chat_with_ollama

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if payload.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == payload.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)

    previous_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at).all()

    history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    reply = chat_with_ollama(
        db=db,
        user_id=current_user.id,
        user_message=payload.message,
        language=payload.language,
        history=history
    )

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
    db.add(ChatMessage(session_id=session.id, role="assistant", content=reply))
    db.commit()

    return ChatResponse(
        session_id=session.id,
        user_message=payload.message,
        assistant_reply=reply
    )


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
def get_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionHistoryResponse(session_id=session.id, messages=session.messages)


@router.get("/sessions")
def get_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()

    return [
        {"session_id": s.id, "created_at": s.created_at, "message_count": len(s.messages)}
        for s in sessions
    ]


@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}