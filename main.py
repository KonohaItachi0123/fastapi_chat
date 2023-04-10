from fastapi import (FastAPI, WebSocket,
                     WebSocketDisconnect, Request, Response, Body)
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


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

templates = Jinja2Templates(directory="templates")


@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/chat")
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender,
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)


@app.get("/api/current_user")
def get_user(request: Request):
    return request.cookies.get("X-Authorization")


class User(BaseModel):
    username: str


@app.post("/api/register")
def testpost(username: User, response: Response):
    response.set_cookie(key="X-Authorization",
                        value=username.username, httponly=True)
    return username
# def register_user(user: RegisterValidator, response: Response):


# fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# @app.post("/items/")
# async def create_item(item : Item) :
#     return item


# @app.get("/items/{item_id}")
# async def read_item(item_id: str, q:str | None = None):
#     if q:
#         return {"item_id" : item_id, "q" : q}
#     return {"item_id" : item_id}

# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]
