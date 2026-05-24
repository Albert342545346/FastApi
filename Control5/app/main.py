from fastapi import FastAPI
import os
from .routers import tasks, users, admin, ws

app = FastAPI()

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(ws.router)

@app.get("/health")
def health_check():
    env = os.getenv("APP_ENV", "local")
    return {"status": "ok", "env": env}