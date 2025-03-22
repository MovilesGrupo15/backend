import uuid
from fastapi import FastAPI, WebSocket
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

@app.get("/api/points")
async def get_points():
    result = []
    min_lat, max_lat = 4.4929, 4.8354
    min_lon, max_lon = -74.2264, -74.0030
    for i in range(random.randint(15,30)):
        image = f"https://picsum.photos/200/300?id={i}"
        result.append({
            "id": str(uuid.uuid4()),
            "name": fake.company(),
            "description": fake.text(),
            "latitude": random.uniform(min_lat, max_lat),
            "longitude": random.uniform(min_lon, max_lon),
            "address": fake.address(),
        })

    return result

@app.get("/api/user")
async def get_user():
    return {
        "userName": fake.name(),
        "points": random.randint(50, 500),

    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)