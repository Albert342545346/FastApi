def test_create_task_success(client):
    resp = client.post("/tasks", json={"title": "Подготовить тесты", "description": "Написать интеграционные тесты", "status": "todo", "priority": 4}, headers={"X-User-Id": "10"})
    assert resp.status_code == 201
    assert resp.json()["id"] == 1
    assert resp.json()["owner_id"] == 10

def test_create_task_title_too_short(client):
    resp = client.post("/tasks", json={"title": "Ab", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    assert resp.status_code == 422

def test_missing_user_id(client):
    resp = client.post("/tasks", json={"title": "Test", "status": "todo", "priority": 1})
    assert resp.status_code == 401

def test_user_sees_only_own_tasks(client):
    client.post("/tasks", json={"title": "User10", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "User11", "status": "todo", "priority": 1}, headers={"X-User-Id": "11"})
    resp = client.get("/tasks", headers={"X-User-Id": "10"})
    assert len(resp.json()) == 1

def test_filter_tasks(client):
    client.post("/tasks", json={"title": "Low", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "High", "status": "done", "priority": 5}, headers={"X-User-Id": "10"})
    assert len(client.get("/tasks?min_priority=4", headers={"X-User-Id": "10"}).json()) == 1
    assert len(client.get("/tasks?status=done", headers={"X-User-Id": "10"}).json()) == 1

def test_update_status(client):
    resp = client.post("/tasks", json={"title": "Upd", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = resp.json()["id"]
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"

def test_get_not_found_or_other_user(client):
    assert client.get("/tasks/999", headers={"X-User-Id": "10"}).status_code == 404
    resp = client.post("/tasks", json={"title": "Other", "status": "todo", "priority": 1}, headers={"X-User-Id": "11"})
    assert client.get(f"/tasks/{resp.json()['id']}", headers={"X-User-Id": "10"}).status_code == 404

def test_delete_task(client):
    resp = client.post("/tasks", json={"title": "Del", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = resp.json()["id"]
    assert client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"}).status_code == 204