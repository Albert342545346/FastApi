import threading
from typing import Dict, List, Optional

class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, dict] = {}
        self._id_counter = 0
        self._lock = threading.Lock()

    def create(self, owner_id: int, title: str, description: Optional[str], status: str, priority: int) -> dict:
        with self._lock:
            self._id_counter += 1
            task = {
                "id": self._id_counter,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "owner_id": owner_id
            }
            self._tasks[task["id"]] = task
            return task

    def get_all(self, owner_id: int, status: Optional[str] = None, min_priority: Optional[int] = None) -> List[dict]:
        with self._lock:
            tasks = [t for t in self._tasks.values() if t["owner_id"] == owner_id]
            if status:
                tasks = [t for t in tasks if t["status"] == status]
            if min_priority is not None:
                tasks = [t for t in tasks if t["priority"] >= min_priority]
            return tasks

    def get_by_id(self, task_id: int, owner_id: int) -> Optional[dict]:
        with self._lock:
            task = self._tasks.get(task_id)
            return task if task and task["owner_id"] == owner_id else None

    def update_status(self, task_id: int, owner_id: int, new_status: str) -> Optional[dict]:
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task["owner_id"] == owner_id:
                task["status"] = new_status
                return task
            return None

    def delete(self, task_id: int, owner_id: int) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task["owner_id"] == owner_id:
                del self._tasks[task_id]
                return True
            return False

    def delete_by_admin(self, task_id: int) -> bool:
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    def get_stats(self) -> dict:
        with self._lock:
            tasks = list(self._tasks.values())
            stats = {"total_tasks": len(tasks), "by_status": {}}
            for t in tasks:
                s = t["status"]
                stats["by_status"][s] = stats["by_status"].get(s, 0) + 1
            return stats