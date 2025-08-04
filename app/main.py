from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.utils import get_version
from app.routes import auth, user, follow, post, like
from app.core.database import engine
from app.models.models import Base

# create DB
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Valenstagram API v   2",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(follow.router)
app.include_router(post.router)
app.include_router(like.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur Valenstagram"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": get_version()}
