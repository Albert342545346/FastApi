from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from typing import List

app = FastAPI()

@app.get("/") # 1.1
async def root():
    return {"message": "Авторелоад действительно работает"}


@app.get("/html") #1.2 
async def html_page():
    return FileResponse("index.html", media_type="text/html")


class Calculation(BaseModel): #1.3 №1
    num1: int
    num2: int 

@app.post("/calculate")
async def calculate(data: Calculation):
    return {"result": data.num1 + data.num2} 


@app.post("/calculate1") # №2
async def calculator(num1: int, num2: int):
    return {"result": num1 + num2}


class User(BaseModel): # 1.4
    name: str
    id: int

@app.get("/users")
async def users():
    return User(name="Ваше Имя и Фамилия", id=1)


class UserWithAge(BaseModel): # 1.5
    name: str
    age: int

@app.post("/user")
async def user(user: UserWithAge):
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": user.age >= 18
    }


class Feedback(BaseModel): # 2.1
    name: str
    message: str

feedback_storage: List[dict] = []

@app.post("/feedback")
async def feedback_message(feedback: Feedback):
    feedback_storage.append({
        "name": feedback.name,
        "message": feedback.message
    })
    
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


class Feedbacks(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

feedback_storage1: List[dict] = []
words = ["кринж", "рофл", "вайб"]

@field_validator("message")
@classmethod
def check_feedbacks_message(cls, v: str):
    message_lower = v.lower()
    for word in words:
        if word in message_lower:
            raise ValueError("Использование недопустимых слов")
    return v

@app.post("/feedbacks")
async def feedbacks_message(feedbacks: Feedbacks):
    feedback_storage1.append({
        "name": feedbacks.name,
        "message": feedbacks.message
    })
    
    return {"message": f"Спасибо, {feedbacks.name}! Ваш отзыв сохранён."}