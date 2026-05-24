import pytest

def test_ws_connect_success(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        ws.send_json({"type": "message", "text": "Hi"})
        assert ws.receive_json()["type"] == "message"

def test_ws_invalid_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/test?username=   ") as ws:
            pass

def test_ws_broadcast_two_clients(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws1:
        with client.websocket_connect("/ws/rooms/test?username=bob") as ws2:
            ws1.send_json({"type": "message", "text": "Broadcast"})
            assert ws1.receive_json()["type"] == "message"
            assert ws2.receive_json()["type"] == "message"

def test_ws_long_message(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        ws.send_json({"type": "message", "text": "A" * 301})
        data = ws.receive_json()
        assert data["type"] == "error"
        assert data["detail"] == "Message is too long"

def test_ws_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws:
        assert "alice" in client.get("/rooms/test/users").json()["users"]
    assert "alice" not in client.get("/rooms/test/users").json()["users"]