import uuid
import time

from fastapi.testclient import TestClient
from main import app, DEVICEID


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
    payload = {
        "motionGravityX": "0",
        DEVICEID: "795F83C8-C2C5-4AE4-8FC9-1770E1ABE23B"
    }

    with TestClient(app) as client:
        response = client.post("/sensor", json=payload)
        time.sleep(2)
        response = client.post("/sensor", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}
    