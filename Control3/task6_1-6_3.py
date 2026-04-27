"""
Объединённое решение: Задания 6.1 + 6.2 + 6.3
"""
import os
import secrets
from typing import Dict
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from passlib.context import CryptContext


# (требование 6.3)
MODE = os.getenv("MODE", "DEV")
DOCS_USER = os.getenv("DOCS_USER", "alimov")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "kr3")


app = FastAPI(
    title="Контрольная работа 3 — Алимов",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: Dict[str, dict] = {}


class UserBase(BaseModel):
    username: str = Field(..., description="Имя пользователя")

class User(UserBase):
    password: str = Field(..., description="Пароль пользователя")

class UserInDB(UserBase):
    hashed_password: str = Field(..., description="Хэш пароля")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def auth_user(credentials: HTTPBasicCredentials = Depends(security)): # аутентификация
    """
    6.1: Извлекает данные из заголовка Authorization
    6.2: Ищет пользователя, проверяет хэш, использует secrets.compare_digest()
    """
    user = None
    for username in fake_users_db:
        if secrets.compare_digest(username, credentials.username):
            user = fake_users_db[username]
            break

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Basic"})
    return user

# 6.2
@app.post("/register", status_code=201)
def register(user: User):
    for username in fake_users_db:
        if secrets.compare_digest(username, user.username):
            raise HTTPException(status_code=409, detail="User already exists")

    user_in_db = UserInDB(
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    fake_users_db[user.username] = user_in_db.model_dump()
    
    return {"message": "User registered successfully!"}

@app.get("/login")
def login(current_user: dict = Depends(auth_user)):
    return {"message": f"Welcome, {current_user['username']}!"}

@app.get("/debug/users")
def debug_get_users():
    """Отладочный эндпоинт: показывает пользователей без хэшей"""
    return {
        username: {"username": data["username"]}
        for username, data in fake_users_db.items()
    }



def verify_docs_access(credentials: HTTPBasicCredentials = Depends(security)):# 6.3
    """Проверка логина/пароля для доступа к документации в DEV-режиме"""
    is_user_correct = secrets.compare_digest(credentials.username, DOCS_USER)
    is_pass_correct = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not (is_user_correct and is_pass_correct):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username

if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    def get_docs(credentials: HTTPBasicCredentials = Depends(security)):
        verify_docs_access(credentials)
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

    @app.get("/openapi.json", include_in_schema=False)
    def get_openapi(credentials: HTTPBasicCredentials = Depends(security)):
        verify_docs_access(credentials)
        return app.openapi()

    @app.get("/redoc", include_in_schema=False)
    def get_redoc():
        raise HTTPException(status_code=404, detail="Not Found")

elif MODE == "PROD":
    @app.get("/docs", include_in_schema=False)
    @app.get("/openapi.json", include_in_schema=False)
    @app.get("/redoc", include_in_schema=False)
    def hide_docs():
        raise HTTPException(status_code=404, detail="Not Found")

else:
    raise ValueError(f"Invalid MODE: {MODE}. Use 'DEV' or 'PROD'")


@app.get("/")
def read_root():
    return {"message": "Server is running", "mode": MODE}