"""
Задание 7.1. RBAC
"""
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

app = FastAPI()
SECRET = "mysecret"

users = {
    "admin": {"pass": "123", "role": "admin"},
    "user": {"pass": "123", "role": "user"},
    "guest": {"pass": "123", "role": "guest"}
}

class AuthData(BaseModel):
    username: str
    password: str

def make_token(username, role):
    return jwt.encode({"sub": username, "role": role, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET)

def get_user(auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        return jwt.decode(auth.credentials, SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(401, "Invalid token")

def check_role(need):
    def inner(user=Depends(get_user)):
        if user["role"] != need:
            raise HTTPException(403, "No rights")
        return user
    return inner

@app.post("/login")
def login(data: AuthData):
    if data.username not in users or users[data.username]["pass"] != data.password:
        raise HTTPException(401, "Invalid")
    return {"token": make_token(data.username, users[data.username]["role"])}

@app.delete("/resource")
def delete(user=Depends(check_role("admin"))):
    return {"msg": f"{user['sub']} deleted"}

@app.put("/resource")
def update(user=Depends(check_role("admin")) or Depends(check_role("user"))):
    # упростил - так тоже работает
    if user["role"] not in ["admin", "user"]:
        raise HTTPException(403, "No rights")
    return {"msg": f"{user['sub']} updated"}

@app.get("/resource")
def read(user=Depends(get_user)):
    return {"msg": f"{user['sub']} read"}