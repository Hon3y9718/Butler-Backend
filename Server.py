from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
import webbrowser
from typing import List
from starlette.websockets import WebSocketDisconnect

edgePath = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edgePath))

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

app = FastAPI(title="Location API")
templates = Jinja2Templates(directory="templates")
isConnected = False

@app.websocket('/ws/{uid}')
async def websocket_endpoint(websocket: WebSocket, uid: str):
    await manager.connect(websocket)
    await manager.broadcast(f"Server: Connected with {uid}")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{uid}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Server: {uid} Disconnected")
    
@app.get("/locate/")
def getLocation(request: Request, uid: str = "unknown"):
    if uid == 'unknown':
        return {
            "error": "The Device is not recognised"
        }
    return templates.TemplateResponse("index.html", {"request": request, "uid": uid})