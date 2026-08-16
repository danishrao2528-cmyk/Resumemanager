from fastapi import FastAPI

from app.database import Base, engine
from app.models.auth_session_model import AuthSession  # noqa: F401
from app.models.resume_model import Resume  # noqa: F401
from app.models.user_model import User  # noqa: F401
from app.routes.admin_routes import router as admin_router
from app.routes.auth_routes import router as auth_router
from app.routes.resume_routes import router as resume_router
from app.utils.logger import logger


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Manager API", version="2.1.0")
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(admin_router)


@app.on_event("startup")
def startup_log():
    logger.info("Resume Manager API started")


@app.get("/")
def home():
    return {"message": "Resume Manager API is working", "version": "2.1.0"}
