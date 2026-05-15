import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestCustomExceptions:
    """Тесты для 10.1: кастомные исключения"""
    def test_condition_a_success(self):
        r = client.get("/check-condition-a", params={"value": 15})
        assert r.status_code == 200

    def test_condition_a_failure(self):
        r = client.get("/check-condition-a", params={"value": 5})
        assert r.status_code == 400
        assert r.json()["code"] == 400

    def test_resource_found(self):
        r = client.get("/search/1")
        assert r.status_code == 200

    def test_resource_not_found(self):
        r = client.get("/search/999")
        assert r.status_code == 404
        assert r.json()["code"] == 404

class TestValidation:
    """Тесты для 10.2: валидация Pydantic"""
    def test_register_success(self):
        payload = {"username": "testuser", "age": 25, "email": "u@ex.com", "password": "12345678"}
        r = client.post("/register", json=payload)
        assert r.status_code == 201
        assert r.json()["phone"] == "Unknown" 

    def test_register_validation_error(self):
        payload = {"username": "t", "age": 10, "email": "bad", "password": "123"}
        r = client.post("/register", json=payload)
        assert r.status_code == 422
        assert r.json()["code"] == 422
        assert len(r.json()["errors"]) > 0