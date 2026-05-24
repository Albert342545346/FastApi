from fastapi import WebSocket
from typing import Dict, List

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][username] = websocket
        await self.broadcast(room_id, {"type": "system", "message": f"{username} joined"})

    async def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            await self.broadcast(room_id, {"type": "system", "message": f"{username} left"})

    async def broadcast(self, room_id: str, payload: dict):
        if room_id not in self.rooms:
            return
        disconnected = []
        for username, ws in self.rooms[room_id].items():
            try:
                await ws.send_json(payload)
            except Exception:
                disconnected.append(username)
        for u in disconnected:
            await self.disconnect(room_id, u)

    def get_users(self, room_id: str) -> List[str]:
        return list(self.rooms.get(room_id, {}).keys())