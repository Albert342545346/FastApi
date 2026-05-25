from fastapi import FastAPI, Response, HTTPException, Header, Cookie, Query, Path, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid
import time
import re
from datetime import datetime
from itsdangerous import Signer, BadSignature

app = FastAPI(title="КР2: Серверные приложения")

# Секретный ключ для подписи куки (используем его во всех заданиях 5.x)
SECRET_KEY = "super_secret_key_for_hw2_2025"
signer = Signer(SECRET_KEY)

# База пользователей для демонстрации аутентификации
USERS_DB = {"user123": "password123", "admin": "admin123"}
ACTIVE_SESSIONS = {}  # Хранилище сессий (в памяти)

# ============================================================================
# 🌟 ЗАДАНИЕ 3.1: Создание пользователя
# ============================================================================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str
    age: Optional[int] = None
    is_subscribed: Optional[bool] = False

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Age must be a positive integer')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

@app.post("/create_user")
def create_user(user: UserCreate):
    return user.model_dump()


# ============================================================================
# 🌟 ЗАДАНИЕ 3.2: Работа с продуктами
# ============================================================================
SAMPLE_PRODUCTS = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

# ⚠️ Важно: маршрут поиска объявляем ПЕРЕД маршрутом с path-параметром,
# чтобы FastAPI не пытался интерпретировать слово "search" как product_id.
@app.get("/products/search")
def search_products(
    keyword: str = Query(...), 
    category: Optional[str] = Query(None), 
    limit: int = Query(10, ge=1)
):
    results = [p for p in SAMPLE_PRODUCTS if keyword.lower() in p["name"].lower() and (category is None or p["category"] == category)]
    return results[:limit]

@app.get("/product/{product_id}")
def get_product(product_id: int = Path(...)):
    for p in SAMPLE_PRODUCTS:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


# ============================================================================
# 🌟 ЗАДАНИЕ 5.1: Простая аутентификация через cookies
# ============================================================================
class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login_51(data: LoginData, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = str(uuid.uuid4())
    ACTIVE_SESSIONS[session_token] = {"username": data.username}
    
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return {"message": "Login successful"}

@app.get("/user")
def get_user_51(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"username": ACTIVE_SESSIONS[session_token]["username"], "profile": {"id": session_token, "status": "active"}}


# ============================================================================
# 🌟 ЗАДАНИЕ 5.2: Аутентификация с подписью (itsdangerous)
# ============================================================================
@app.post("/login52")
def login_52(data: LoginData, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(uuid.uuid4())
    # itsdangerous.Signer автоматически создает формат: <user_id>.<signature>
    signed_token = signer.sign(user_id)
    
    response.set_cookie(key="session_token", value=signed_token, httponly=True, max_age=3600)
    return {"message": "Login successful"}

@app.get("/profile")
def get_profile_52(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # unsign проверяет подпись и возвращает исходные данные
        user_id = signer.unsign(session_token).decode('utf-8')
    except BadSignature:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    return {"username": "authenticated_user", "user_id": user_id, "profile": "active"}


# ============================================================================
# 🌟 ЗАДАНИЕ 5.3: Динамическое время жизни сессии
# ============================================================================
MAX_SESSION_TIME = 300   # 5 минут
RENEW_THRESHOLD = 180    # 3 минуты

@app.post("/login53")
def login_53(data: LoginData, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(uuid.uuid4())
    timestamp = int(time.time())
    payload = f"{user_id}.{timestamp}"
    signed_token = signer.sign(payload)  # формат: user_id.timestamp.signature
    
    response.set_cookie(key="session_token", value=signed_token, httponly=True, secure=False, max_age=MAX_SESSION_TIME)
    return {"message": "Login successful"}

@app.get("/profile53")
def get_profile_53(session_token: Optional[str] = Cookie(None), response: Response = None):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        payload = signer.unsign(session_token).decode('utf-8')
        user_id, ts_str = payload.split(".")
        last_activity = int(ts_str)
    except (BadSignature, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session")

    current_time = int(time.time())
    time_passed = current_time - last_activity

    # Сессия истекла
    if time_passed >= MAX_SESSION_TIME:
        raise HTTPException(status_code=401, detail="Session expired")

    # Продление сессии (прошло от 3 до 5 минут)
    if RENEW_THRESHOLD <= time_passed < MAX_SESSION_TIME:
        new_ts = int(time.time())
        new_payload = f"{user_id}.{new_ts}"
        new_token = signer.sign(new_payload)
        response.set_cookie(key="session_token", value=new_token, httponly=True, secure=False, max_age=MAX_SESSION_TIME)

    return {
        "username": "authenticated_user",
        "user_id": user_id,
        "last_activity": last_activity,
        "time_passed_seconds": time_passed,
        "message": "Session active"
    }


# ============================================================================
# 🌟 ЗАДАНИЕ 5.4: Работа с HTTP-заголовками
# ============================================================================
@app.get("/headers")
def get_headers(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Missing required headers: User-Agent and Accept-Language")
    
    pattern = r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?(,[a-zA-Z]{2}(-[a-zA-Z]{2})?(;q=[0-9]\.[0-9])?)*$'
    if not re.match(pattern, accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")
    
    return {"User-Agent": user_agent, "Accept-Language": accept_language}


# ============================================================================
# 🌟 ЗАДАНИЕ 5.5: Переиспользуемая модель заголовков (Pydantic)
# ============================================================================
class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")

    @field_validator('accept_language')
    @classmethod
    def validate_lang(cls, v):
        pattern = r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?(,[a-zA-Z]{2}(-[a-zA-Z]{2})?(;q=[0-9]\.[0-9])?)*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format')
        return v

# Dependency для внедрения модели
def get_common_headers(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language")
) -> CommonHeaders:
    return CommonHeaders(user_agent=user_agent, accept_language=accept_language)

@app.get("/headers55")
def get_headers_55(headers: CommonHeaders = Depends(get_common_headers)):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}

@app.get("/info")
def get_info(headers: CommonHeaders = Depends(get_common_headers), response: Response = None):
    server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    response.headers["X-Server-Time"] = server_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }