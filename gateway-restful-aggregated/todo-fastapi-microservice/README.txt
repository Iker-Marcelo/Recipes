pip install fastapi uvicorn httpx
uvicorn main:app --reload


Explanation:
Model Definition: We define a TodoItem class using Pydantic, which is used for data validation and settings management using Python type annotations.

API Endpoints:

@app.post("/todos/"): Adds a new TODO item to the list.
@app.get("/todos/"): Retrieves the list of all TODO items.
@app.put("/todos/{todo_id}"): Updates an existing TODO item by ID.
@app.delete("/todos/{todo_id}"): Deletes a TODO item by ID.
In-Memory Database: This example uses a simple list (database) to store TODO items. In a real-world application, you would replace this with a database system.

Response Models: By specifying response_model, FastAPI will automatically convert the output data to its declared type.

Error Handling: HTTP exceptions are raised when, for example, an item is not found during update or delete operations.

OpenAPI Compatibility: FastAPI automatically generates an OpenAPI schema for your API, accessible at /docs (Swagger UI) or /redoc endpoints.

To run this API, you would need to have FastAPI and uvicorn installed. You can run the server with a command like:
