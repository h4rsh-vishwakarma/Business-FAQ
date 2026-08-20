from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import configure_database, get_db, init_db
from app.models import Lead
from app.schemas import ChatMessage, ChatResponse, HealthResponse, LeadOut
from app.services.chat_engine import ChatEngine
from app.services.knowledge_base import load_faqs


security = HTTPBasic()


def create_app() -> FastAPI:
    configure_database(settings.database_url)
    init_db()

    app = FastAPI(
        title="Business FAQ & Lead Capture Chatbot",
        version="1.0.0",
        description="Restaurant demo chatbot for customer support and lead capture.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    faqs = load_faqs(settings.faq_path)
    engine = ChatEngine(settings.demo_business_name, faqs)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
        valid_user = secrets.compare_digest(credentials.username, settings.admin_username)
        valid_pass = secrets.compare_digest(credentials.password, settings.admin_password)
        if not (valid_user and valid_pass):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials.",
                headers={"WWW-Authenticate": "Basic"},
            )

    @app.get("/", response_class=HTMLResponse)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/admin/leads", response_class=HTMLResponse)
    def leads_dashboard(_: None = Depends(require_admin)) -> FileResponse:
        return FileResponse(static_dir / "admin.html")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", business=settings.demo_business_name)

    @app.post("/chat", response_model=ChatResponse)
    def chat(payload: ChatMessage, db: Session = Depends(get_db)) -> ChatResponse:
        result = engine.respond(db, payload.session_id, payload.message)
        return ChatResponse(session_id=payload.session_id, **result)

    @app.get("/api/leads", response_model=list[LeadOut])
    def list_leads(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> list[LeadOut]:
        leads = db.scalars(select(Lead).order_by(Lead.created_at.desc())).all()
        return [LeadOut.model_validate(lead) for lead in leads]

    @app.get("/api/embed.js")
    def embed_script() -> Response:
        content = (static_dir / "widget.js").read_text(encoding="utf-8")
        return Response(content=content, media_type="application/javascript")

    return app


app = create_app()
