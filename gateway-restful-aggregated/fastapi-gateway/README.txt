uvicorn main:app --reload --port 8080

1: Set Up the FastAPI Project for the API Gateway
First, create a new Python project and install FastAPI and httpx, an HTTP client for Python:

mkdir fastapi-gateway
cd fastapi-gateway
pip install fastapi uvicorn httpx


2: Create the Gateway
Create a file named gateway.py:

from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

# Define the microservices URLs
TODO_SERVICE_URL = "http://localhost:8000"
USER_SERVICE_URL = "http://localhost:3000"

# HTTP Client
client = httpx.Client()

@app.api_route("/todos/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def todo_service_proxy(path: str, request: Request):
    return await proxy_request(request, TODO_SERVICE_URL)

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(path: str, request: Request):
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


3: Run the Gateway
Run the API gateway:


uvicorn main:app --reload --port 8080