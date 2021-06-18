# main.py
import time, asyncio
from typing import Any, Dict
from datetime import date, datetime, time, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException

app = FastAPI()

POLL_SPEED = 0
DELETE_DATA_TIME = 5*60 # 5min
DELETE_POLL_SPEED = 10
DEVICEID = 'identifierForVendor'


from uuid import UUID

# https://stackoverflow.com/questions/19989481/how-to-determine-if-a-string-is-a-valid-v4-uuid
# CC Martin Thoma
def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


@app.get('/')
async def hello():
    return {'message': 'Sensor 2 Cables works'}


@app.post('/sensor')
async def push_sensor_data(data: Dict[Any, Any] = None):

    deviceid = data.get(DEVICEID)
    if not deviceid:
        raise HTTPException(status_code=422, detail="Missing identifierForVendor (device uuid)")

    deviceid = deviceid.lower()
    if not is_valid_uuid(deviceid):
        raise HTTPException(status_code=422, detail="Invalid identifierForVendor (device uuid)")

    newDevice = False
    if not app.state.sensors.get(deviceid):
        newDevice = True

    app.state.sensors[deviceid] = {
        'data': data,
        'has_changed': True,
        'updated_at': datetime.now()
    }

    # We need a way to trigger old value deletion
    if newDevice:
        await check_remove_old_data()

    return {"message": "ok"}
    

async def get_data(deviceid: str):
    return app.state.sensors.get(deviceid).get('data')


@app.websocket("/ws/{deviceid}")
async def websocket_endpoint(websocket: WebSocket, deviceid: str):
    deviceid = deviceid.lower()
    if deviceid not in app.state.sensors:
        await websocket.close()
        return
    try:
        await websocket.accept()
        while True:
            if app.state.sensors[deviceid]['has_changed']:
                data = await get_data(deviceid)
                await websocket.send_json(data)
                app.state.sensors[deviceid]['has_changed'] = False
            else:
                await asyncio.sleep(POLL_SPEED)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        await websocket.close()


async def check_remove_old_data(duration=DELETE_DATA_TIME):
    threshold = datetime.now() - timedelta(seconds=duration)
    to_del = []
    for deviceid, d in app.state.sensors.items():
        # print(d['updated_at'], threshold)
        if d['updated_at'] < threshold:
            to_del.append(deviceid)

    for deviceid in to_del:
        del app.state.sensors[deviceid]

    # Empty, stop polling
    if not app.state.sensors:
        return
 
    # Wait and call again
    # await asyncio.sleep(DELETE_POLL_SPEED)
    # await check_remove_old_data()


@app.on_event("startup")
async def startup_event():
    app.state.sensors = {}