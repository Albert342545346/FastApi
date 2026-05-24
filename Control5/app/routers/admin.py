from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import require_admin, get_storage, TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_stats(admin: dict = Depends(require_admin), storage: TaskStorage = Depends(get_storage)):
    return storage.get_stats()

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task_admin(task_id: int, admin: dict = Depends(require_admin), storage: TaskStorage = Depends(get_storage)):
    if not storage.delete_by_admin(task_id):
        raise HTTPException(status_code=404, detail="Task not found")