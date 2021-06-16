# main.py
import time, asyncio
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

POLL_SPEED = 0

@app.get('/')
async def hello():
    return {'message': 'Sensor 2 Cables works'}


@app.post('/sensor')
async def push_sensor_data(data: Dict[Any, Any] = None):
    app.state.sensor = data
    app.state.has_changed = True
    

async def get_data():
    return app.state.sensor


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            if app.state.has_changed:
                data = await get_data()
                await websocket.send_json(data)
                app.state.has_changed = False
            else:
                await asyncio.sleep(POLL_SPEED)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        await websocket.close()


@app.on_event("startup")
async def startup_event():
    app.state.sensor = None
    app.state.has_changed = False