def test_users_me(client):
    resp = client.get("/users/me", headers={"X-User-Id": "5"})
    assert resp.status_code == 200 and resp.json()["id"] == 5

def test_missing_user_id(client):
    assert client.get("/users/me").status_code == 401

def test_admin_stats_forbidden(client):
    assert client.get("/admin/stats", headers={"X-User-Id": "5", "X-User-Role": "user"}).status_code == 403

def test_admin_stats_success(client):
    client.post("/tasks", json={"title": "T", "status": "todo", "priority": 1}, headers={"X-User-Id": "5"})
    resp = client.get("/admin/stats", headers={"X-User-Id": "99", "X-User-Role": "admin"})
    assert resp.status_code == 200 and "total_tasks" in resp.json()

def test_normal_user_cant_delete_other_task(client):
    resp = client.post("/tasks", json={"title": "My", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    assert client.delete(f"/tasks/{resp.json()['id']}", headers={"X-User-Id": "11"}).status_code == 404

def test_admin_can_delete_other_task(client):
    resp = client.post("/tasks", json={"title": "Admin target", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    assert client.delete(f"/admin/tasks/{resp.json()['id']}", headers={"X-User-Id": "99", "X-User-Role": "admin"}).status_code == 204

def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200 and resp.json()["status"] == "ok"