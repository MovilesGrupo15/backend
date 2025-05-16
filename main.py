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


@app.get("/api/recycling-guide")
async def get_recycling_guide():
    """
    Obtiene la guía de reciclaje con información detallada sobre diferentes tipos de residuos.
    """
    recycling_guide = [
        {
            "id": "plastic-1",
            "title": "Botellas PET",
            "wasteType": "Plástico tipo 1 (PET)",
            "category": "Plástico",
            "description": "Las botellas PET son ampliamente utilizadas para bebidas y son 100% reciclables. Identificables por el número 1 en el símbolo de reciclaje.",
            "instructions": "1. Vaciar completamente\n2. Enjuagar\n3. Quitar etiquetas\n4. Aplastar para reducir volumen",
            "resourceUrl": "https://example.com/pet-recycling"
        },
        {
            "id": "plastic-2",
            "title": "Bolsas plásticas",
            "wasteType": "Polietileno",
            "category": "Plástico",
            "description": "Las bolsas plásticas típicas son de polietileno. Su reciclaje es más complejo que otros plásticos, pero posible.",
            "instructions": "1. Asegurarse que estén limpias y secas\n2. Agrupar varias bolsas juntas\n3. Llevar a puntos especiales de recolección",
            "resourceUrl": "https://example.com/plastic-bags"
        },
        {
            "id": "plastic-3",
            "title": "Envases de yogur y helado",
            "wasteType": "Plástico tipo 5 (PP)",
            "category": "Plástico",
            "description": "Los envases de polipropileno son comunes en la industria alimentaria y son reciclables.",
            "instructions": "1. Enjuagar bien\n2. Quitar etiquetas si es posible\n3. Separar tapas si son de material diferente",
            "resourceUrl": ""
        },
        {
            "id": "paper-1",
            "title": "Papel de oficina",
            "wasteType": "Papel blanco",
            "category": "Papel",
            "description": "El papel de oficina es fácilmente reciclable y puede ser convertido en nuevo papel, reduciendo la tala de árboles.",
            "instructions": "1. Quitar grapas, clips y plásticos\n2. Evitar papel sucio con alimentos\n3. Mantener separado de otros tipos de papel",
            "resourceUrl": "https://example.com/office-paper"
        },
        {
            "id": "paper-2",
            "title": "Cartón corrugado",
            "wasteType": "Cartón",
            "category": "Papel",
            "description": "El cartón corrugado es uno de los materiales más reciclados en el mundo. Se puede reciclar hasta 7 veces.",
            "instructions": "1. Desarmar las cajas\n2. Quitar cintas adhesivas\n3. Mantener seco\n4. Aplanar para ahorrar espacio",
            "resourceUrl": ""
        },
        {
            "id": "paper-3",
            "title": "Periódicos y revistas",
            "wasteType": "Papel impreso",
            "category": "Papel",
            "description": "Los periódicos y revistas son fáciles de reciclar y se convierten en nuevos productos de papel.",
            "instructions": "1. Mantener secos\n2. No mezclar con papel blanco\n3. Quitar grapas de revistas\n4. Pueden incluirse insertos publicitarios",
            "resourceUrl": ""
        },
        {
            "id": "glass-1",
            "title": "Botellas de vidrio",
            "wasteType": "Vidrio",
            "category": "Vidrio",
            "description": "El vidrio es 100% reciclable y puede ser reciclado infinitamente sin perder calidad o pureza.",
            "instructions": "1. Vaciar completamente\n2. Enjuagar\n3. Separar por colores si es posible\n4. No incluir vidrios de ventanas o espejos",
            "resourceUrl": "https://example.com/glass-recycling"
        },
        {
            "id": "glass-2",
            "title": "Frascos de alimentos",
            "wasteType": "Vidrio de conservas",
            "category": "Vidrio",
            "description": "Los frascos de vidrio para conservas, mermeladas y otros alimentos son totalmente reciclables.",
            "instructions": "1. Quitar etiquetas si es posible\n2. Enjuagar bien\n3. Separar tapas metálicas\n4. Agrupar por colores",
            "resourceUrl": ""
        },
        {
            "id": "metal-1",
            "title": "Latas de aluminio",
            "wasteType": "Aluminio",
            "category": "Metal",
            "description": "Las latas de aluminio son altamente reciclables. Reciclar aluminio requiere sólo el 5% de la energía necesaria para producir aluminio nuevo.",
            "instructions": "1. Vaciar y enjuagar\n2. Aplastar para ahorrar espacio\n3. No es necesario quitar etiquetas",
            "resourceUrl": "https://example.com/aluminum-cans"
        },
        {
            "id": "metal-2",
            "title": "Latas de conservas",
            "wasteType": "Acero y hojalata",
            "category": "Metal",
            "description": "Las latas de conservas están hechas principalmente de acero con una capa de estaño, son completamente reciclables.",
            "instructions": "1. Enjuagar bien\n2. Quitar etiquetas\n3. Aplastar si es posible\n4. No es necesario quitar la etiqueta pequeña del fondo",
            "resourceUrl": ""
        },
        {
            "id": "metal-3",
            "title": "Chatarra pequeña",
            "wasteType": "Metales diversos",
            "category": "Metal",
            "description": "Pequeños objetos metálicos del hogar como llaves viejas, herramientas rotas, etc.",
            "instructions": "1. Separar por tipo de metal si es posible\n2. Quitar partes no metálicas\n3. Agrupar objetos pequeños\n4. Llevar a punto de recolección especializado",
            "resourceUrl": ""
        },
        {
            "id": "organic-1",
            "title": "Residuos de alimentos",
            "wasteType": "Orgánico",
            "category": "Orgánico",
            "description": "Los residuos orgánicos pueden ser compostados para crear abono natural para plantas y jardines.",
            "instructions": "1. Separar de otros residuos\n2. Usar en compostaje doméstico o municipal\n3. Evitar incluir carne o lácteos en compostaje casero",
            "resourceUrl": "https://example.com/composting"
        },
        {
            "id": "organic-2",
            "title": "Poda y jardín",
            "wasteType": "Residuos verdes",
            "category": "Orgánico",
            "description": "Restos de poda, hojas secas, césped cortado y otros residuos del jardín.",
            "instructions": "1. Triturar ramas grandes\n2. Mezclar hojas secas con residuos húmedos\n3. Usar para compostaje\n4. Algunos municipios ofrecen recolección especial",
            "resourceUrl": ""
        },
        {
            "id": "electronic-1",
            "title": "Teléfonos y computadoras",
            "wasteType": "Electrónico",
            "category": "Electrónico",
            "description": "Los dispositivos electrónicos contienen materiales valiosos y también componentes tóxicos que requieren un manejo especial.",
            "instructions": "1. Nunca tirar a la basura regular\n2. Borrar datos personales\n3. Llevar a puntos de recolección de residuos electrónicos\n4. Consultar con el fabricante sobre programas de devolución",
            "resourceUrl": "https://example.com/e-waste"
        },
        {
            "id": "electronic-2",
            "title": "Baterías",
            "wasteType": "Residuo peligroso",
            "category": "Electrónico",
            "description": "Las baterías contienen metales pesados y químicos que pueden contaminar suelos y aguas.",
            "instructions": "1. Nunca tirar a la basura regular\n2. Almacenar en contenedor no metálico\n3. Llevar a puntos específicos de recolección de baterías",
            "resourceUrl": "https://example.com/battery-disposal"
        },
        {
            "id": "electronic-3",
            "title": "Electrodomésticos pequeños",
            "wasteType": "Aparatos eléctricos",
            "category": "Electrónico",
            "description": "Aparatos como tostadoras, licuadoras, planchas contienen metales recuperables y componentes que requieren tratamiento especial.",
            "instructions": "1. Separar cables si están dañados\n2. Quitar baterías si las tiene\n3. Llevar a centro de recepción de electrodomésticos\n4. Algunos contienen materiales valiosos como cobre",
            "resourceUrl": ""
        },
        {
            "id": "special-1",
            "title": "Bombillas LED y fluorescentes",
            "wasteType": "Residuo especial",
            "category": "Especial",
            "description": "Las bombillas, especialmente las fluorescentes, contienen mercurio y requieren manejo especial.",
            "instructions": "1. NUNCA romper las bombillas\n2. Guardar en empaque original si es posible\n3. Llevar a punto de recolección especializado\n4. Las LED son menos tóxicas pero también deben reciclarse",
            "resourceUrl": ""
        },
        {
            "id": "special-2",
            "title": "Aceites de cocina",
            "wasteType": "Aceite usado",
            "category": "Especial",
            "description": "Los aceites de cocina usados pueden convertirse en biodiesel o jabón, pero no deben ir por el desagüe.",
            "instructions": "1. Dejar enfriar completamente\n2. Colar para quitar restos de comida\n3. Almacenar en recipiente cerrado\n4. Llevar a punto de recolección específico",
            "resourceUrl": ""
        },
        {
            "id": "special-3",
            "title": "Medicamentos vencidos",
            "wasteType": "Farmacéutico",
            "category": "Especial",
            "description": "Los medicamentos vencidos pueden ser tóxicos para el medio ambiente y no deben ir a la basura común.",
            "instructions": "1. NO tirar por el inodoro\n2. Quitar información personal de envases\n3. Llevar a farmacia con programa de recolección\n4. Algunos hospitales tienen puntos de recepción",
            "resourceUrl": ""
        }
    ]
    
    return JSONResponse(recycling_guide)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)