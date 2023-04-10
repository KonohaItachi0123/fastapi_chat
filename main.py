from fastapi import (FastAPI, WebSocket, WebSocketDisconnect, Request)
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name : str
    description : str | None = None
    price : float
    tax : float | None = None

class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection[0].send_json(data)    

manager = SocketManager()

app = FastAPI()



fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.post("/items/")
async def create_item(item : Item) :
    return item

@app.get("/")
async def read_root():
    return {"Hello1": "World1112"}

@app.get("/items/{item_id}")
async def read_item(item_id: str, q:str | None = None):
    if q:
        return {"item_id" : item_id, "q" : q}    
    return {"item_id" : item_id}

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

