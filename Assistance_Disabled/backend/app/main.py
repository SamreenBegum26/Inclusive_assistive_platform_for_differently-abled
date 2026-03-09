from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

# All model imports
from app.modules.users.models import User
from app.modules.assistive.models import SpeechLog
from app.modules.routines import models as routine_models
from app.modules.schemes.models import GovernmentScheme
from app.modules.chatbot.models import ChatSession, ChatMessage


# All router imports
from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.assistive.routes import router as assistive_router
from app.modules.routines.routes import router as routine_router
from app.modules.schemes.routes import router as schemes_router
from app.modules.chatbot.routes import router as chatbot_router


app = FastAPI(title="Assistive Platform API")

# ✅ Middleware FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routers AFTER middleware
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(assistive_router, prefix="/assistive", tags=["Assistive"])
app.include_router(routine_router, prefix="/routines", tags=["Routines"])
app.include_router(schemes_router, prefix="/schemes", tags=["Government Schemes"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])


@app.get("/")
def health_check():
    return {"status": "API running successfully"}

# ✅ Tables created ONCE here
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)