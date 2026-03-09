import requests
from sqlalchemy.orm import Session
from app.modules.schemes.models import GovernmentScheme
from app.modules.routines.models import RoutineTask

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma2:2b"

LANGUAGE_PROMPTS = {
    "en": "Always respond in English.",
    "hi": "हमेशा हिंदी में जवाब दें।",
    "te": "ఎల్లప్పుడూ తెలుగులో సమాధానం ఇవ్వండి.",
}


def get_schemes_context(db: Session, disability_type: str = None) -> str:
    if disability_type:
        schemes = db.query(GovernmentScheme).filter(
            GovernmentScheme.disability_type.in_([disability_type, "all"])
        ).all()
    else:
        schemes = db.query(GovernmentScheme).all()

    if not schemes:
        return "No government schemes available."

    context = "AVAILABLE GOVERNMENT SCHEMES FOR DISABLED PERSONS IN INDIA:\n\n"
    for s in schemes:
        context += f"- {s.name} ({s.disability_type}): {s.description} Eligibility: {s.eligibility} Link: {s.official_link}\n"
    return context


def get_user_tasks_context(db: Session, user_id: int) -> str:
    tasks = db.query(RoutineTask).filter(
        RoutineTask.assigned_to == user_id
    ).all()

    if not tasks:
        return "No tasks assigned to this user yet."

    context = "USER'S ASSIGNED TASKS:\n\n"
    for t in tasks:
        status = "✅ Completed" if t.completed else "⏳ Pending"
        context += f"- {t.title} | Category: {t.category} | Time: {t.scheduled_time} | Status: {status}\n"
    return context


def build_system_prompt(db: Session, user_id: int, language: str) -> str:
    language_instruction = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["en"])
    schemes_context = get_schemes_context(db)
    tasks_context = get_user_tasks_context(db, user_id)

    return f"""You are a helpful assistant for disabled persons in India.
You help users understand government schemes and benefits,
help them manage daily tasks and routines, and provide general support.
Be kind, patient, simple and clear in your responses.
{language_instruction}

{schemes_context}

{tasks_context}

When asked about schemes, always mention eligibility and how to apply.
When asked about tasks, refer to the user's assigned tasks above.
Keep responses concise and easy to understand.
"""


def chat_with_ollama(
    db: Session,
    user_id: int,
    user_message: str,
    language: str,
    history: list
) -> str:
    system_prompt = build_system_prompt(db, user_id, language)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return "Sorry, I am having trouble responding right now. Please try again."

    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running. Please start Ollama and try again."
    except requests.exceptions.Timeout:
        return "⏱️ Response took too long. Please try a shorter question."
    except Exception as e:
        return f"❌ Error: {str(e)}"