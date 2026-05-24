from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from ..dependencies import get_current_user, get_storage, TaskStorage
from ..schemas import TaskCreate, TaskUpdateStatus, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, storage: TaskStorage = Depends(get_storage), user: dict = Depends(get_current_user)):
    return storage.create(user["id"], task.title, task.description, task.status, task.priority)

@router.get("/", response_model=list[TaskResponse])
def list_tasks(status: Optional[str] = Query(None), min_priority: Optional[int] = Query(None), storage: TaskStorage = Depends(get_storage), user: dict = Depends(get_current_user)):
    return storage.get_all(user["id"], status, min_priority)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, storage: TaskStorage = Depends(get_storage), user: dict = Depends(get_current_user)):
    task = storage.get_by_id(task_id, user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, status_update: TaskUpdateStatus, storage: TaskStorage = Depends(get_storage), user: dict = Depends(get_current_user)):
    task = storage.update_status(task_id, user["id"], status_update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, storage: TaskStorage = Depends(get_storage), user: dict = Depends(get_current_user)):
    if not storage.delete(task_id, user["id"]):
        raise HTTPException(status_code=404, detail="Task not found")