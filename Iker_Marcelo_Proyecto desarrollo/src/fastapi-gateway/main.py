import logging
from fastapi import FastAPI, Query, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

import httpx, os
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from urllib.parse import quote

logging.basicConfig(level=logging.DEBUG)

# Retrieve environment variables with default values
TODO_SERVICE_URL = os.getenv('TODO_SERVICE_URL', 'http://localhost:8000')
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:3000/api/user')

SECRET_KEY = "secret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    
# Define the function to revoke a token
def revoke_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Aquí puedes implementar la lógica para revocar el token,
        # por ejemplo, guardarlo en una lista o base de datos de tokens revocados.
        print(f"Token revoked: {token}")
        return {"message": "Token revoked successfully"}
    except jwt.JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        print(f"Error during token revocation: {str(e)}")
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** and **register** logic is here.",
    },
    {
        "name": "todos",
        "description": "Manage TODO items.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect root to index.html
@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index.html")

# You can also add a specific endpoint for todos.html if needed
@app.get("/todos-page")
async def read_todos():
    return RedirectResponse(url="/static/todos.html")


client = httpx.Client()

# Models for user authentication
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class WelcomeRequest(BaseModel):
    user: str


@app.post("/auth/register", tags=["users"], status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    response = client.post(f"{AUTH_SERVICE_URL}/register", json=user.dict())

    if response.status_code == 201:
        return {"message": "User registered successfully"}
    elif response.status_code == 409:
        raise HTTPException(status_code=409, detail="User already exists")
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/auth/login", tags=["users"])
async def login_user(user: UserLogin):
    response = client.post(f"{AUTH_SERVICE_URL}/login", json=user.dict())
    print(response)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/auth/revoke-token", tags=["users"])
async def revoke_token(request: Request):
    # Obtén el token del encabezado de autorización
    authorization_header = request.headers.get('Authorization')

    if not authorization_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Extrae el token del encabezado
    token = authorization_header.replace('Bearer ', '').strip()

    # Realiza la solicitud al servicio de autenticación para revocar el token
    response = client.post(f"{AUTH_SERVICE_URL}/revoke-token", headers={"Authorization": f"Bearer {token}"})

    # Verifica el código de estado de la respuesta
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    

# TODOs endpoints

@app.get("/welcome", tags=["welcome"])
async def welcome(request: Request, user: str = Query(..., alias="user")):
    # Obtén el nombre de usuario desde el parámetro de consulta en la URL
    username = user

    welcome_message_with_username = f"Bienvenido, {username}!"

    # Devuelve una respuesta JSON con las cabeceras CORS adecuadas
    return JSONResponse(content={"message": welcome_message_with_username}, headers={"Access-Control-Allow-Origin": "*"})

# Obtener la lista de categorías, áreas e ingredientes
@app.get("/list/{category}", tags=["todos"], response_model=list)
async def get_list(category: str):
    response = client.get(f"{TODO_SERVICE_URL}/list/{category}")
    response.raise_for_status()  # Asegúrate de manejar errores HTTP
    return response.json()

# Endpoint para obtener recetas por ingrediente
@app.get("/recipes/by-ingredient/{ingredient}", tags=["todos"], response_model=list)
async def get_recipes_by_ingredient(ingredient: str):
    response = client.get(f"{TODO_SERVICE_URL}/recipes/by-ingredient/{ingredient}")
    response.raise_for_status()  # Asegúrate de manejar errores HTTP
    return response.json()

# Endpoint para obtener recetas por categoría
@app.get("/recipes/by-category/{category}", tags=["todos"], response_model=list)
async def get_recipes_by_category(category: str):
    response = client.get(f"{TODO_SERVICE_URL}/recipes/by-category/{category}")
    response.raise_for_status()  # Asegúrate de manejar errores HTTP
    return response.json()

# Endpoint para obtener recetas por área
@app.get("/recipes/by-area/{area}", tags=["todos"], response_model=list)
async def get_recipes_by_area(area: str):
    response = client.get(f"{TODO_SERVICE_URL}/recipes/by-area/{area}")
    response.raise_for_status()  # Asegúrate de manejar errores HTTP
    return response.json()

# Endpoint para obtener receta aleatoria
@app.get("/recipes/random-meal")
async def get_random_meal():
    response = client.get(f"{TODO_SERVICE_URL}/recipes/random-meal")
    response.raise_for_status()
    return response.json()


# Define the /auth/revoke-token route
@app.post("/auth/revoke-token")
async def revoke_token_route(token: str = Depends(oauth2_scheme)):
    return revoke_token(token)
    

'''
@app.get("/todos/", tags=["todos"])
async def get_todos():
    response = client.get(f"{TODO_SERVICE_URL}/todos/")
    return response.json()
'''


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)