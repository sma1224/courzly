from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime
import uuid

from database.connection import get_redis

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Active connections: workflow_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Status connections: workflow_id -> list of websockets
        self.status_connections: Dict[str, List[WebSocket]] = {}
        # User mapping: websocket -> user_id
        self.user_mapping: Dict[WebSocket, str] = {}
        # Workflow user tracking: workflow_id -> set of user_ids
        self.workflow_users: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, workflow_id: str, user_id: str = None):
        """Connect a websocket to a workflow chat"""
        await websocket.accept()
        
        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = []
            self.workflow_users[workflow_id] = set()
        
        self.active_connections[workflow_id].append(websocket)
        
        if user_id:
            self.user_mapping[websocket] = user_id
            self.workflow_users[workflow_id].add(user_id)
        
        # Notify others about new connection
        await self.broadcast_system_message(workflow_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "active_users": list(self.workflow_users[workflow_id])
        }, exclude_websocket=websocket)
        
        logger.info(f"WebSocket connected to workflow {workflow_id}, user: {user_id}")

    async def connect_status(self, websocket: WebSocket, workflow_id: str):
        """Connect a websocket for workflow status updates"""
        await websocket.accept()
        
        if workflow_id not in self.status_connections:
            self.status_connections[workflow_id] = []
        
        self.status_connections[workflow_id].append(websocket)
        logger.info(f"Status WebSocket connected to workflow {workflow_id}")

    def disconnect(self, websocket: WebSocket, workflow_id: str):
        """Disconnect a websocket from workflow chat"""
        if workflow_id in self.active_connections:
            if websocket in self.active_connections[workflow_id]:
                self.active_connections[workflow_id].remove(websocket)
                
                # Remove user from tracking
                user_id = self.user_mapping.pop(websocket, None)
                if user_id and workflow_id in self.workflow_users:
                    self.workflow_users[workflow_id].discard(user_id)
                
                # Clean up empty lists
                if not self.active_connections[workflow_id]:
                    del self.active_connections[workflow_id]
                    if workflow_id in self.workflow_users:
                        del self.workflow_users[workflow_id]
                else:
                    # Notify others about disconnection
                    asyncio.create_task(self.broadcast_system_message(workflow_id, {
                        "type": "user_left",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "active_users": list(self.workflow_users[workflow_id])
                    }))
        
        logger.info(f"WebSocket disconnected from workflow {workflow_id}")

    def disconnect_status(self, websocket: WebSocket, workflow_id: str):
        """Disconnect a status websocket"""
        if workflow_id in self.status_connections:
            if websocket in self.status_connections[workflow_id]:
                self.status_connections[workflow_id].remove(websocket)
                
                if not self.status_connections[workflow_id]:
                    del self.status_connections[workflow_id]

    async def handle_message(self, workflow_id: str, message: str, sender_websocket: WebSocket):
        """Handle incoming message and broadcast to others"""
        try:
            data = json.loads(message)
            user_id = self.user_mapping.get(sender_websocket)
            
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": workflow_id
            })
            
            # Store in Redis for persistence
            await self.store_message(workflow_id, data)
            
            # Broadcast to all connections except sender
            await self.broadcast_message(workflow_id, data, exclude_websocket=sender_websocket)
            
            # Handle special message types
            if data.get("type") == "typing_indicator":
                # Don't store typing indicators, just broadcast
                pass
            elif data.get("type") == "ai_query":
                # Trigger AI response
                await self.trigger_ai_response(workflow_id, data)
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from workflow {workflow_id}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def broadcast_message(self, workflow_id: str, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast message to all connections in a workflow"""
        if workflow_id not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.active_connections[workflow_id]:
            if websocket == exclude_websocket:
                continue
                
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket, workflow_id)

    async def broadcast_system_message(self, workflow_id: str, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast system message (user join/leave, etc.)"""
        message["type"] = message.get("type", "system")
        message["is_system"] = True
        await self.broadcast_message(workflow_id, message, exclude_websocket)

    async def broadcast_status_update(self, workflow_id: str, status_data: dict):
        """Broadcast workflow status update"""
        if workflow_id not in self.status_connections:
            return
        
        message = {
            "type": "status_update",
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            **status_data
        }
        
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.status_connections[workflow_id]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending status update: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect_status(websocket, workflow_id)

    async def store_message(self, workflow_id: str, message: dict):
        """Store message in Redis for persistence"""
        try:
            redis_client = await get_redis()
            key = f"chat:{workflow_id}"
            
            # Store message with expiration (30 days)
            await redis_client.lpush(key, json.dumps(message))
            await redis_client.expire(key, 30 * 24 * 3600)
            
            # Keep only last 1000 messages
            await redis_client.ltrim(key, 0, 999)
            
        except Exception as e:
            logger.error(f"Error storing message: {e}")

    async def get_recent_messages(self, workflow_id: str, limit: int = 50) -> List[dict]:
        """Get recent messages from Redis"""
        try:
            redis_client = await get_redis()
            key = f"chat:{workflow_id}"
            
            messages = await redis_client.lrange(key, 0, limit - 1)
            return [json.loads(msg) for msg in reversed(messages)]
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            return []

    def get_active_users(self, workflow_id: str) -> List[str]:
        """Get list of active users in a workflow"""
        return list(self.workflow_users.get(workflow_id, set()))

    def get_connection_count(self, workflow_id: str) -> int:
        """Get number of active connections for a workflow"""
        return len(self.active_connections.get(workflow_id, []))

    async def trigger_ai_response(self, workflow_id: str, user_message: dict):
        """Trigger AI response to user message"""
        try:
            from workflows.ai_chat import generate_ai_response
            
            # Generate AI response
            ai_response = await generate_ai_response(workflow_id, user_message["message"])
            
            # Create AI message
            ai_message = {
                "id": str(uuid.uuid4()),
                "user_id": None,  # AI message
                "message": ai_response,
                "type": "ai_response",
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": workflow_id,
                "is_ai": True,
                "metadata": {"triggered_by": user_message["id"]}
            }
            
            # Store and broadcast AI response
            await self.store_message(workflow_id, ai_message)
            await self.broadcast_message(workflow_id, ai_message)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            
            # Send error message
            error_message = {
                "id": str(uuid.uuid4()),
                "user_id": None,
                "message": "Sorry, I'm having trouble responding right now. Please try again.",
                "type": "ai_error",
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": workflow_id,
                "is_ai": True
            }
            
            await self.broadcast_message(workflow_id, error_message)

# Global connection manager instance
connection_manager = ConnectionManager()