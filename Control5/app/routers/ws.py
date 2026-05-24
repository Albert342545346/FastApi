from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..manager import RoomManager

router = APIRouter()
room_manager = RoomManager()

@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = Query(None)):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    await room_manager.connect(room_id, username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                text = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({"type": "error", "detail": "Message is too long"})
                else:
                    await room_manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username)

@router.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    return {"room_id": room_id, "users": room_manager.get_users(room_id)}