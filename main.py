from fastapi import FastAPI
import logging
from app.database import Base, engine
from app.models.resume_model import Resume
from app.routes.resume_routes import router as resume_router

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Manager API")

app.include_router(resume_router)


@app.get("/")
def home():
    return {"message": "API is working"}
