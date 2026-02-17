from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

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


class UserWithAge(BaseModel):
    name: str
    age: int

@app.post("/user")
async def user(user: UserWithAge):
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": user.age >= 18
    }
