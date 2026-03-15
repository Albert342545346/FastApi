from fastapi import FastAPI, HTTPException, Query, Cookie, Depends, status, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uuid

app = FastAPI()
security = HTTPBasic()


class UserCreate(BaseModel): # 3.1
    name: str
    email: EmailStr
    age: int
    is_subscribed: bool


@app.post("/create_user")
def user(user: UserCreate):
    return {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed
    }


class Product(BaseModel): # 3.2
    product_id: int
    name: str
    category: str
    price: float


sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

@app.get("/products/search")
def get_search(
    keyword: str = Query(...),
    category: Optional[str] = Query(None),
    limit: int = Query(10)
):
    results = []
    for p in sample_products:
        if keyword.lower() not in p["name"].lower():
            continue
        if category and p["category"].lower() != category.lower():
            continue
        results.append(p)
    return results[:limit]


@app.get("/product/{product_id}")
def get_product(product_id: int):
    for p in sample_products:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Продукт не найден")


sessions = {} # 5.1

VALID_USER = {
    "username": "user123",
    "password": "password123"
}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(response: Response, credentials: LoginRequest):

    # Вход в систему.
    # Если логин/пароль верны — устанавливает cookie session_token.

    # Проверка учётных данных
    if credentials.username != VALID_USER["username"] or credentials.password != VALID_USER["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Генерация уникального токена
    token = str(uuid.uuid4())
    
    # Сохранение сессии
    sessions[token] = credentials.username
    
    # Установка cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,      # недоступен для JavaScript
        max_age=1800,       # время жизни: 30 минут
        samesite="lax"      # защита от CSRF
    )
    
    return {"message": "Login successful"}


@app.get("/user")
async def get_user(request: Request):
    # Защищённый маршрут.Требует валидный cookie session_token.
    # Получаем токен из cookie
    token = request.cookies.get("session_token")
    
    # Проверка: есть ли токен и валиден ли он
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})
    
    return {
        "username": sessions[token],
        "message": "User authenticated successfully"
    }


@app.post("/logout")
async def logout(response: Response):
    # Выход из системы — удаляет cookie.
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}