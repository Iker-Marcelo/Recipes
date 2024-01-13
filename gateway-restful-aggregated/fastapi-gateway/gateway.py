import logging
from fastapi import FastAPI, Request, HTTPException, status
import httpx
import pydantic


app = FastAPI()

# Define the microservices URLs
TODO_SERVICE_URL = "http://localhost:8000"
USER_SERVICE_URL = "http://localhost:3000"

# HTTP Client
client = httpx.Client()

logging.basicConfig(level=logging.DEBUG)

# Rutas de proxy para TODOs
@app.api_route("/todos/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def todo_service_proxy(path: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

@app.route("/welcome", methods=["GET"])
async def welcome_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

@app.api_route("/list/{category}", methods=["GET"])
async def list_proxy(category: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

@app.api_route("/recipes/by-ingredient/{ingredient}", methods=["GET"])
async def recipes_by_ingredient_proxy(ingredient: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)


@app.api_route("/recipes/by-category/{category}", methods=["GET"])
async def recipes_by_category_proxy(category: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

@app.api_route("/recipes/by-area/{area}", methods=["GET"])
async def recipes_by_area_proxy(area: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

# Nueva ruta para obtener una receta aleatoria
@app.api_route("/recipes/random-meal", methods=["GET"])
async def recipe_service_proxy(request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

# Rutas de proxy para usuarios
@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(path: str, request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

# Rutas de proxy para autenticación
@app.route("/auth/register", methods=["POST"])
async def auth_register_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

@app.route("/auth/login", methods=["POST"])
async def auth_login_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

# Ruta de proxy para revocar el token
@app.route("/auth/revoke-token", methods=["POST"])
async def auth_revoke_token(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)


async def proxy_request(request: Request, service_url: str):
    method = request.method
    url = f"{service_url}/{request.url.path}"
    headers = dict(request.headers)
    content = await request.body()

    try:
        response = await client.request(method, url, headers=headers, content=content)
        return response.content, response.status_code, response.headers.items()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=8080, reload=True)

