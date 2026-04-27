from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

database.init_db()
app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Todo(BaseModel):
    title: str
    description: str = None

@app.post("/register")
def register(user: User):
    if not database.create_user(user.username, user.password):
        raise HTTPException(400, "User exists")
    return {"message": "User registered"}

@app.post("/todos")
def create(todo: Todo):
    id = database.create_todo(todo.title, todo.description)
    return {"id": id, "title": todo.title, "description": todo.description, "completed": False}

@app.get("/todos/{id}")
def read(id: int):
    row = database.get_todo(id)
    if not row:
        raise HTTPException(404, "Not found")
    return {"id": row[0], "title": row[1], "description": row[2], "completed": bool(row[3])}

@app.put("/todos/{id}")
def update(id: int, todo: Todo):
    database.update_todo(id, todo.title, todo.description)
    return {"message": "Updated"}

@app.delete("/todos/{id}")
def delete(id: int):
    database.delete_todo(id)
    return {"message": "Deleted"}