"""
WebSocket Connection Manager

Manages WebSocket connections for real-time updates.
"""

from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        # session_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Send a message to all connections in a session."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        await websocket.send_json(message)
