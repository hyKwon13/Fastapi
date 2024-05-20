from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

connected_websockets = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)