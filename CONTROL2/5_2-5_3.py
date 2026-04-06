from fastapi import FastAPI, HTTPException, Cookie, Request, Response
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import uuid

SECRET_KEY = "your-secret-key-change-this"
SALT = "session-cookie-salt"
serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY, salt=SALT)

USERS_DB = {
    "user": {"username": "user", "password": "password", "id": str(uuid.uuid4())},
    "admin": {"username": "admin", "password": "admin123", "id": str(uuid.uuid4())}
}

class Login(BaseModel):
    username: str
    password: str

app = FastAPI()

@app.post("/login_2")
def login(body: Login, response: Response):
    user = USERS_DB.get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = user["id"]
    token = serializer.dumps(user_id)
    
    response.set_cookie(
        key="session_token",
        value=token,
        max_age=1800,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"message": "Login successful"}

@app.get("/profile")
def get_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    try:
        user_id = serializer.loads(session_token, max_age=1800)
        for item in USERS_DB.values():
            if item["id"] == user_id:
                return {"profile": {"username": item["username"], "id": item["id"]}}
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    except (BadSignature, SignatureExpired):
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session_token")
    return {"message": "Logged out"}