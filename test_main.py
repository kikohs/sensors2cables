import uuid
import time

from fastapi.testclient import TestClient
from main import app, DEVICEID

DEFAULT_DEVICEID = "795F83C8-C2C5-4AE4-8FC9-1770E1ABE23B".lower()

TEST_PAYLOAD = {
    "motionGravityX": 0,
    DEVICEID: DEFAULT_DEVICEID
}

def test_main_route():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Sensor 2 Cables works"}


def test_missing_deviceid():
    with TestClient(app) as client:
        response = client.post("/sensor",
            json={"motionGravityX": "0"}
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "Missing identifierForVendor (device uuid)"}


def test_exist_valid_deviceid():
    payload = TEST_PAYLOAD
    with TestClient(app) as client:
        response = client.post("/sensor", json=payload)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}
    

# def test_websocket():
#     with TestClient(app) as client:
#         response = client.post("/sensor", json=TEST_PAYLOAD)
#         with client.websocket_connect(f"/ws/{DEFAULT_DEVICEID}") as websocket:
#             data = websocket.receive_json()
#             assert data == {"motionGravityX": 1, DEVICEID: DEFAULT_DEVICEID}
#             return