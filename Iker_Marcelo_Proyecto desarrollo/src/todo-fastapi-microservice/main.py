from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import requests
import httpx
import logging
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta


app = FastAPI()

# Conexión a MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')

# Crear la base de datos y la colección
db = mongo_client['recipe_cache']
cache_collection = db['recipe_cache_collection']

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.DEBUG)


# Fake user authentication just for demonstration
def get_current_user(username: str = Depends(lambda x: "Usuario")):
    return username

# Función para obtener la lista de categorías, áreas o ingredientes
def get_list(category):
    url = f"https://www.themealdb.com/api/json/v1/1/list.php?{category}=list"
    response = requests.get(url)
    data = response.json()
    return data

# Función para filtrar por ingrediente, categoría o área
def filter_by(category, value):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?{category}={value}"
    response = requests.get(url)
    data = response.json()
    return data

# Función para obtener el cliente httpx
async def get_httpx_client():
    async with httpx.AsyncClient() as client:
        yield client

# Modelo para los datos de recetas
class RecipeData(BaseModel):
    idMeal: str
    strMeal: str
    strCategory: str
    strArea: str
    strInstructions: str
    strMealThumb: str
    strTags: str
    strYoutube: str
    ingredients: List[dict]
    strSource: str

THEMEALDB_RANDOM_URL = "https://www.themealdb.com/api/json/v1/1/random.php"


# Obtener la lista de categorías
categories = get_list("c")
print("Categorías disponibles:")
for category in categories["meals"]:
    print(category["strCategory"])

# Obtener la lista de áreas
areas = get_list("a")
print("\nÁreas disponibles:")
for area in areas["meals"]:
    print(area["strArea"])

# Obtener la lista de ingredientes
ingredients = get_list("i")
print("\nIngredientes disponibles:")
for ingredient in ingredients["meals"]:
    print(ingredient["strIngredient"])


@app.get("/", response_model=dict)
async def welcome_user(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user}!"}

# Obtener la lista de categorías, áreas e ingredientes
@app.get("/list/{category}", response_model=List[dict])
def get_list(category: str):
    url = f"https://www.themealdb.com/api/json/v1/1/list.php?{category}=list"
    response = requests.get(url)
    data = response.json()
    return data["meals"]

# Endpoint para obtener recetas por ingrediente
@app.get("/recipes/by-ingredient/{ingredient}", response_model=List[dict])
def get_recipes_by_ingredient(ingredient: str):
    # Aquí llamamos a la función filter_by con el ingrediente específico
    filtered_recipes = filter_by("i", ingredient)
    return filtered_recipes["meals"]

# Endpoint para obtener recetas por categoría
@app.get("/recipes/by-category/{category}", response_model=List[dict])
def get_recipes_by_category(category: str):
    # Aquí llamamos a la función filter_by con la categoría específica
    filtered_recipes = filter_by("c", category)
    return filtered_recipes["meals"]

# Endpoint para obtener recetas por área
@app.get("/recipes/by-area/{area}", response_model=List[dict])
def get_recipes_by_area(area: str):
    # Aquí llamamos a la función filter_by con el área específica
    filtered_recipes = filter_by("a", area)
    return filtered_recipes["meals"]

# Endpoint para obtener una receta aleatoria global
@app.get("/recipes/random-meal", response_model=RecipeData)
async def get_random_meal(
    client: httpx.AsyncClient = Depends(get_httpx_client),
):
    try:
        # Comprobar si hay una entrada en la base de datos para una receta aleatoria en el último intervalo de tiempo
        cache_entry = cache_collection.find_one({"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}})

        if cache_entry:
            print("Retrieving data from MongoDB (global)")
            # Si hay una entrada en la base de datos, devolver los datos almacenados
            return RecipeData(**cache_entry)

        print("Fetching data from TheMealDB API")
        # Obtener datos de una receta aleatoria
        response = await client.get(THEMEALDB_RANDOM_URL)
        response.raise_for_status()
        meal_data = response.json()['meals'][0]

        print("Meal Data:", meal_data)  # Añadir log de depuración

        # Mapear datos a nuestro modelo RecipeData
        recipe = RecipeData(
            idMeal=meal_data['idMeal'],
            strMeal=meal_data['strMeal'],
            strCategory=meal_data['strCategory'],
            strArea=meal_data['strArea'],
            strInstructions=meal_data['strInstructions'],
            strMealThumb=meal_data['strMealThumb'],
            strTags=meal_data['strTags'],
            strYoutube=meal_data['strYoutube'],
            ingredients=[
                {"name": meal_data[f'strIngredient{i}'], "measure": meal_data[f'strMeasure{i}']}
                for i in range(1, 21) if meal_data[f'strIngredient{i}']
            ],
            strSource=meal_data.get('strSource', '')
        )

        # Almacenar la nueva entrada en la base de datos
        cache_collection.insert_one({"timestamp": datetime.utcnow(), **recipe.dict()})

        return recipe

    except httpx.RequestError as exc:
        # Captura errores relacionados con solicitudes HTTP (por ejemplo, problemas de conexión)
        raise HTTPException(status_code=500, detail=f"Request error: {str(exc)}")
    except httpx.HTTPStatusError as exc:
        # Captura errores relacionados con códigos de estado HTTP no exitosos
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {str(exc)}")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

