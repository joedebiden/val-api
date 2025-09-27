from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import fast_mqtt
from app.core.utils import get_version
from app.routes import auth, user, follow, post, like, comment, message
from app.core.database import engine
from app.models.models import Base

# create DB
Base.metadata.create_all(bind=engine)



@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await fast_mqtt.mqtt_startup()
    yield
    await fast_mqtt.mqtt_shutdown()
app = FastAPI(
    title="Valenstagram API v2",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=_lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    print("Connected to MQTT Broker")
    client.subscribe("chat/+/messages")

@fast_mqtt.on_message()
def messages(client, topic, payload, qos, properties):
    print(f"Message reçu: {payload} sur {topic}")

@app.post("/ssage/send-me")
async def send_message(topic: str, message: str):
    fast_mqtt.publish(topic, message)
    return {"status": "message sent"}

# Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(follow.router)
app.include_router(post.router)
app.include_router(like.router)
app.include_router(comment.router)
app.include_router(message.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur Valenstagram"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": get_version()}
