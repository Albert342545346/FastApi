from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional


class ErrorResponse(BaseModel):
    detail: str
    code: int
    errors: Optional[list] = None


class CustomExceptionA(Exception):
    def __init__(self, detail: str = "Условие A не выполнено"):
        self.detail = detail
        self.status_code = 400
        super().__init__(self.detail)

class CustomExceptionB(Exception):
    def __init__(self, detail: str = "Ресурс не найден"):
        self.detail = detail
        self.status_code = 404
        super().__init__(self.detail)

app = FastAPI(title="KR4 - Tasks 10.1 & 10.2")


@app.exception_handler(CustomExceptionA)
async def handle_exception_a(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, code=exc.status_code).model_dump()
    )

@app.exception_handler(CustomExceptionB)
async def handle_exception_b(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, code=exc.status_code).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def handle_validation(request: Request, exc: RequestValidationError):
    formatted_errors = [
        {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Validation Error",
            code=422,
            errors=formatted_errors
        ).model_dump()
    )


class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'


@app.get("/")
def read_root():
    return {
        "message": "Control Work #4 is running",
        "docs": "/docs",
        "tasks": ["9.1: Alembic migrations", "10.1: Custom exceptions", "10.2: Pydantic validation", "11.1+11.2: Sync & Async tests"]
    }

@app.get("/check-condition-a")
def check_condition_a(value: int = 5):
    """Вызывает CustomExceptionA, если value < 10"""
    if value < 10:
        raise CustomExceptionA(f"Значение {value} меньше требуемого минимума (10)")
    return {"status": "success", "message": "Условие A выполнено"}

@app.get("/search/{item_id}")
def search_item(item_id: int):
    """Вызывает CustomExceptionB, если ID нет в базе"""
    existing_items = {1: "Ноутбук", 2: "Смартфон", 3: "Планшет"}
    if item_id not in existing_items:
        raise CustomExceptionB(f"Товар с ID {item_id} не найден в каталоге")
    return {"item_id": item_id, "name": existing_items[item_id]}

@app.post("/register", response_model=User, status_code=201)
def register(user: User):
    """Принимает JSON, валидирует через Pydantic, возвращает пользователя"""
    return user