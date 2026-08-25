# Tender Status Tracking Microservice (Task 6)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Backend microservice for managing tenders and automatically tracking their status change audit trail history built with **FastAPI**, **SQLModel / SQLAlchemy 2.0 (Async)**, **Alembic**, and **Docker**.

> **Полная документация решения, описание логики и алгоритмов**: См. [LOGIC.md](LOGIC.md)


---

---

## Quick Start

### 1. Set environment variables
Copy template `.env.example` to `.env`:
```sh
cp .env.example .env
```

### 2. Run with Docker Compose
```sh
docker compose up -d --build
```
*(or using Makefile: `make run-dev-build`)*

### 3. Run Alembic Migrations & Seed Initial Data
```sh
docker compose exec fastapi_server alembic upgrade head
docker compose exec fastapi_server python app/initial_data.py
```
*(or using Makefile: `make init-db`)*

### 4. Interactive API Documentation (Swagger UI)
Open in browser: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Testing

Run integration tests for tender status lifecycle:
```sh
pytest app/test/api/test_tender.py
```
*(or inside Docker: `make pytest`)*

---

---

---

## Code Quality & Linting

This project uses **Black** for code formatting and **Flake8** for linting. 
A Git pre-push hook is configured to automatically run these checks before every push. 
Code checks are also executed automatically on GitHub Actions.

Run linters manually:
`sh
# Format code with Black
poetry run black .

# Check code with Flake8
poetry run flake8 . --max-line-length=120 --exclude=.venv,__pycache__,alembic/versions
`

---

## License

This project is licensed under the terms of the **[MIT License](LICENSE)**.
