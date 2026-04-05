from fastapi import FastAPI, HTTPException, Query, Cookie, Depends, status, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uuid

app = FastAPI()
security = HTTPBasic()


class UserCreate(BaseModel): # 3.1
    name: str
    email: EmailStr
    age: int | None = Field(default=None, gt=0)
    is_subscribed: bool | None = None


@app.post("/create_user")
def create_user(user: UserCreate):
    return {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed
    }



sample_products = [ # 3.2
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


@app.get("/product/{product_id}")
def product(product_id: int):
    for item in sample_products:
        if item["product_id"] == product_id:
            return item
    raise HTTPException(status_code=404, detail="Продукт не найден")


@app.get("/products/search")
def get_search(
    keyword: str = Query(...),
    category: str | None = None,
    limit: int | None = Query(10, ge=1)
):
    results = []
    for p in sample_products:
        if keyword.lower() not in p["name"].lower():
            continue
        if category:
            if p["category"].lower() != category.lower():
                continue
        results.append(p)
    return results[:limit]



sessions = {} # 5.1

USER_DATA = {
    "username": "user",
    "password": "password"
}


class Login(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(body: Login, response: Response):
    if body.username != USER_DATA["username"] or body.password != USER_DATA["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = uuid.uuid4().hex

    response.set_cookie(
        key="session_token",
        value=token,
        max_age=1800,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Login successful"}
