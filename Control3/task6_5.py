from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import secrets
from collections import defaultdict
import time

app = FastAPI()

SECRET = "mysecret"
ALGO = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {} 

requests_log = defaultdict(list)

def rate_limit(key: str, max_req: int, window: int):
    now = time.time()
    requests_log[key] = [t for t in requests_log[key] if now - t < window]
    if len(requests_log[key]) >= max_req:
        raise HTTPException(429, "Too many requests")
    requests_log[key].append(now)

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


@app.post("/register")
def register(data: AuthData, req: Request):
    rate_limit(req.client.host, 1, 60)  # 1 запрос в минуту
    
    for u in users:
        if secrets.compare_digest(u, data.username):
            raise HTTPException(409, "User already exists")
    
    users[data.username] = pwd_context.hash(data.password)
    return {"message": "New user created"}


@app.post("/login")
def login(data: AuthData, req: Request):
    rate_limit(req.client.host, 5, 60)
    
    if data.username not in users:
        raise HTTPException(404, "User not found")
    
    if not pwd_context.verify(data.password, users[data.username]):
        raise HTTPException(401, "Authorization failed")
    
    return {"access_token": make_token(data.username), "token_type": "bearer"}

@app.get("/protected_resource")
def protected(user: str = Depends(get_user)):
    return {"message": f"Welcome {user}!"}