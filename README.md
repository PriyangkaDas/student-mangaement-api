# Student Record Management API

A production-grade RESTful API built with *FastAPI, **SQLAlchemy ORM, and **SQLite, secured with **OAuth2 & JWT authentication* and containerized with *Docker*.

---

## Features

- *Persistent Relational Storage:* SQLite database management using SQLAlchemy 2.0 ORM.
- *Strict Data Validation:* High-integrity schema enforcement and boundary constraints using Pydantic v2.
- *JWT Authentication:* OAuth2 Password Bearer flow with signed JSON Web Tokens for role-based route protection (POST, PUT, DELETE).
- *Dynamic Query Filtering:* Filter student records by department branch and minimum CGPA criteria.
- *Performance Profiling:* Custom HTTP middleware recording request processing latency (X-Process-Time).
- *Interactive Documentation:* Automatic OpenAPI generation via Swagger UI (/docs) and ReDoc (/redoc).
- *Containerized:* Docker-ready for consistent cross-platform deployment.

---

## Tech Stack

- *Backend Framework:* FastAPI
- *ORM / Database:* SQLAlchemy, SQLite
- *Validation:* Pydantic v2
- *Security:* PyJWT, OAuth2
- *ASGI Server:* Uvicorn
- *DevOps:* Docker
---

## API Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /login | Authenticate and obtain JWT access token | Public |
| GET | / | Health check endpoint | Public |
| GET | /students | Retrieve all students (supports branch & min_cgpa filters) | Public |
| GET | /students/{roll_no} | Retrieve a specific student by roll number | Public |
| POST | /students | Register a new student | *Admin Only (Bearer Token)* |
| PUT | /students/{roll_no} | Update existing student records | *Admin Only (Bearer Token)* |
| DELETE | /students/{roll_no} | Permanently remove a student | *Admin Only (Bearer Token)* |

---

## Local Setup & Run

### 1. Clone the Repository
```bash
git clone [https://github.com/PriyangkaDas/student-mangaement-api.git](https://github.com/PriyangkaDas/student-mangaement-api.git)
cd student-mangaement-api

2. Install Dependencies
pip install -r requirement.txt

3.Run the Development Server
uvicorn database_api:app --reload

Access the interactive API documentation at:
Swagger UI:
http://127.0.0.1:8000/docs
reDoc:
http://127.0.0.1:8000/redoc

Docker Deployment
to build and run the application inside a container:
docker build -t student-api .
docker run -p 8000:8000 student-api


---

## API Endpoints
