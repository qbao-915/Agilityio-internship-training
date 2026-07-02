# 🚀 FastAPI CRUD Demo Application

A clean, minimalist FastAPI application implementing standard CRUD operations with an in-memory mock database to observe HTTP methods, status codes, and JSON serialization/deserialization.

---

## 🛠️ Tech Stack & Core Features
* **Backend Framework:** FastAPI (Python)
* **Server:** Uvicorn (ASGI)
* **Features:** Comprehensive input validation (using Pydantic), dynamic sequential ID generation, pagination filtering, and flexible search capabilities by either ID or string name.

---

## 📂 Project Structure

To ensure easy management and modularity, the application routes are divided into separate modules using FastAPI's `APIRouter`:

```text
Day-5-FastAPI-Demo/
├── routers/
│   ├── __init__.py
│   ├── hello.py       # General endpoints (e.g., GET /hello)
│   └── items.py       # Items CRUD endpoints, Pydantic schemas, and mock database
├── main.py            # Main application mounting the routers
└── README.md          # Project documentation
```

---

## 🌐 REST Standards Compliance

This API is designed to align with **REST (Representational State Transfer) Level 2 standards** (Richardson Maturity Model):

* **Resources & Plural URIs**: Items are modeled as collections, using the plural noun endpoint `/items` instead of the singular `/item`.
* **HTTP Verbs**: Standard HTTP methods are used for their intended purposes: `GET` for retrieval, `POST` for creation, `PUT` for updates, and `DELETE` for removal.
* **JSON Request Bodies**: Instead of passing data via URL query parameters, `POST` and `PUT` accept structured JSON payloads in the request body (validated using Pydantic).
* **Appropriate HTTP Status Codes**: Successful creation returns `201 Created`, successful queries/updates/deletions return `200 OK`, and bad requests or missing resources yield `400 Bad Request` or `404 Not Found`.
* **Flexible Identification**: To provide maximum client flexibility, lookups (`GET`, `PUT`, `DELETE`) accept both numeric IDs (e.g., `/items/1`) and name strings (e.g., `/items/Apple`) as path parameters.

---

## 📑 API Endpoints Documentation

### 1. General Info
* **`GET /hello`**
  * **Description:** Returns a simple JSON greetings object.
  * **Response (200 OK):** `{"message": "Hello World"}`

### 2. Create Operation
* **`POST /items`**
  * **Description:** Creates and adds a new item with an auto-incrementing sequential ID.
  * **Request Body (JSON):**
    ```json
    {
      "item_name": "Apple"
    }
    ```
  * **Validation:** Rejects empty inputs, auto-strips leading/trailing whitespaces, and prevents duplicate item names.
  * **Response (201 Created):** `{"item_id": 1, "item_name": "Apple"}`
  * **Errors:** `400 Bad Request` (Empty name or duplicate entry), `422 Unprocessable Entity` (Missing/invalid request body).

### 3. Read Operation (with Pagination & Single Retrieve)
* **`GET /items?skip=1&limit=10`**
  * **Description:** Retrieves sorted items list from the database using offset-based pagination.
  * **Query Parameters:**
    * `skip` (int): Page index (must be greater than 0, default is 1).
    * `limit` (int): Maximum number of records to return (default is 10).
  * **Response (200 OK):** `[{"item_id": 1, "item_name": "Apple"}]`

* **`GET /items/{item_id_or_name}`**
  * **Description:** Retrieves details of a specific item.
  * **Flexibility:** Accepts either the item's integer ID or its string name path parameter.
  * **Response (200 OK):** `{"item_id": 1, "item_name": "Apple"}`
  * **Errors:** `404 Not Found`.

### 4. Update Operation
* **`PUT /items/{item_id_or_name}`**
  * **Description:** Updates the name of an existing item.
  * **Flexibility:** Accepts either the item's integer ID or its string name path parameter.
  * **Request Body (JSON):**
    ```json
    {
      "item_name": "Banana"
    }
    ```
  * **Validation:** Rejects empty names, exact identical modifications, or names that collide with another existing item.
  * **Response (200 OK):** `{"item_id": 1, "item_name": "Banana"}`
  * **Errors:** `400 Bad Request` (Invalid input logic) or `404 Not Found`.

### 5. Delete Operation
* **`DELETE /items/{item_id_or_name}`**
  * **Description:** Permanently removes an item from the list.
  * **Flexibility:** Dynamically matches against either the integer ID or string name.
  * **Response (200 OK):** `{"message": "Item Apple deleted successfully"}`
  * **Errors:** `404 Not Found` (If no item matches the provided criteria).

---

## 💻 How to Run the Project Locally

### 1. Install Dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

### 2. Start the Development Server:
Navigate into the Day-5-FastAPI-Demo directory and run Uvicorn:
   ```bash
   cd exercises/Day-5-FastAPI-Demo
   uvicorn main:app --reload
   ```

### 3. Interact and Explore:
- Open <http://127.0.0.1:8000/hello> in your browser to verify the connection.
- Access the interactive API documentation at <http://127.0.0.1:8000/docs> to test all CRUD operations directly inside the Swagger UI.