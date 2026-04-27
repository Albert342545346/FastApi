"""
Задание 6.4. JWT-аутентификация
"""
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

app = FastAPI()

SECRET = "mysecret"
ALGO = "HS256"

users = {
    "Vova": "1234",
    "Sonya": "zxc"
}

class AuthData(BaseModel):
    username: str
    password: str

def make_token(username: str):
    return jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET, algorithm=ALGO
    )

def get_user(auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        data = jwt.decode(auth.credentials, SECRET, algorithms=[ALGO])
        return data["sub"]
    except:
        raise HTTPException(401, "Invalid or expired token")

@app.post("/login")
def login(data: AuthData):
    if data.username not in users or users[data.username] != data.password:
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": make_token(data.username), "token_type": "bearer"}

@app.get("/protected_resource")
def protected(user: str = Depends(get_user)):
    return {"message": f"Welcome {user}!"}