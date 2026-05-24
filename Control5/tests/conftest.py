import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import task_storage

@pytest.fixture
def client():
    task_storage._tasks.clear()
    task_storage._id_counter = 0
    with TestClient(app) as c:
        yield c