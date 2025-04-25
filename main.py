import httpx
import json
import uuid
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
import random
import uvicorn
from faker import Faker
fake = Faker()

app = FastAPI()

@app.websocket("/detect")
async def detect_objects(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive image bytes
            image_bytes = await websocket.receive_bytes()
            
            # Mock detection - generate random bounding boxes
            num_objects = random.randint(1, 5)
            recycling_types = ["plastic", "paper", "glass", "metal", "organic"]
            
            detection_results = []
            for _ in range(num_objects):
                # Generate random bbox coordinates (x, y, width, height)
                x = random.random()
                y = random.random()
                width = random.random()
                height = random.random()
                
                # Random confidence score
                confidence = round(random.uniform(0.7, 0.99), 2)
                
                # Random recycling type
                obj_type = random.choice(recycling_types)
                
                detection_results.append({
                    "bbox": [x, y, width, height],
                    "type": obj_type,
                    "confidence": confidence
                })
            
            # Send detection results back
            await websocket.send_json(detection_results)
            
    except Exception as e:
        await websocket.close(code=1000, reason=str(e))


@app.get("/api/offers")
async def get_offers():
    result = []
    for i in range(random.randint(5,10)):
        image = f"https://picsum.photos/200/300?id={i}"
        result.append({
            "id": str(uuid.uuid4()),
            "description": fake.text(),
            "points": random.randint(50, 500),
            "imageUrl": image,
            "backgroundColor": random.randint(0x000000, 0xFFFFFF)
        })

    return result

# Base URL for the API
BASE_POSCONSUMO = "https://visorgeo.ambientebogota.gov.co/api/v1/posconsumo_vista"

BASE_RESIDUOS = "https://visorgeo.ambientebogota.gov.co/api/v1/residuo/?format=json"

@app.get("/api/points")
async def get_points():
    url = f"{BASE_POSCONSUMO}/"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    data = resp.json()
    objects = data.get("objects", [])
    result = []
    for obj in objects:
        coords = obj.get("geom", {}).get("coordinates", [None, None])
        lon, lat = coords[0], coords[1]
        result.append({
            "id":        str(obj.get("gid", uuid.uuid4())),
            "name":      obj.get("nombre", ""),
            "description": obj.get("residuo_nombre", ""),
            "latitude":  lat,
            "longitude": lon,
            "address":   obj.get("direccion", ""),
            "horario": obj.get("horario", "Horario no disponible"),
        })
    return JSONResponse(result)


@app.get("/api/points/{point_id}")
async def get_point_detail(point_id: int):
    url = f"{BASE_POSCONSUMO}/{point_id}/"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Point not found")
        resp.raise_for_status()
    return JSONResponse(content=resp.json())


@app.get("/api/user")
async def get_user():
    return {
        "userName": fake.name(),
        "points": random.randint(50, 500),

    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)