# Qortex — Music Catalog Manager

A music catalog management application built with Django REST Framework + Vue 3 (Quasar + Tailwind). Manage artists, albums, and songs with track numbering.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL 15 |
| Frontend | Vue 3, Vite, Quasar, Tailwind CSS |
| State Management | Pinia |
| HTTP Client | Axios |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |

## Features

- **Artists** — full CRUD (create, read, update, delete)
- **Albums** — full CRUD with artist association and release year
- **Songs** — full CRUD, songs can belong to multiple albums
- **Album ↔ Song management** — add/remove songs to albums with track numbers (through model)
- **Search & filter** — DRF search and ordering on all list endpoints
- **Admin panel** — Django admin for manual data management
- **Seeded sample data** — catalog pre-populated with artists, albums, and songs via `python manage.py seed`

## Project Structure

```
qortex/
├── backend/                # Django REST API (complete)
│   ├── qortex/             # Django project settings
│   ├── musiq_catalog/      # Catalog app (models, views, serializers)
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── API_CONTRACT.md
├── frontend/               # Vue 3 SPA
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI
├── docker-compose.yml      # Multi-service orchestration
├── .gitignore
└── README.md
```

## Local Setup (without Docker)

### Prerequisites

- Python 3.10+
- Node 18+
- PostgreSQL

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit if needed
python manage.py migrate
python manage.py seed
python manage.py runserver
```

To re-seed (wipe and replace existing data):

```bash
python manage.py seed --force
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env  # edit if needed
npm run dev
```

### Access

- Backend API: http://localhost:8000/api
- Frontend: http://localhost:5173

## Docker Setup

```bash
docker compose up -d --build
```

### Access

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- Admin panel: http://localhost:8000/admin/

### Commands

| Command | Description |
|---------|-------------|
| `docker compose up -d --build` | Build and start all services |
| `docker compose down` | Stop all services |
| `docker compose down -v` | Stop and remove DB volume (resets all data) |
| `docker compose logs -f backend` | Follow backend logs |
| `docker compose exec backend python manage.py seed --force` | Re-seed sample data (wipes existing) |
| `docker compose exec backend python manage.py createsuperuser` | Create admin user |

## API Documentation

Full API contract is available at [backend/API_CONTRACT.md](backend/API_CONTRACT.md).

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET / POST | `/api/artists/` | List / create artists |
| GET / PUT / DELETE | `/api/artists/<id>/` | Retrieve / update / delete artist |
| GET | `/api/artists/<id>/albums/` | List albums by artist |
| GET / POST | `/api/albums/` | List / create albums |
| GET / PUT / DELETE | `/api/albums/<id>/` | Retrieve / update / delete album |
| GET / POST | `/api/albums/<id>/songs/` | List / add songs to album |
| DELETE | `/api/albums/<id>/songs/<song_id>/` | Remove song from album |
| GET / POST | `/api/songs/` | List / create songs |
| GET / PUT / DELETE | `/api/songs/<id>/` | Retrieve / update / delete song |

All list endpoints support `?search=`, `?ordering=`, `?page=`, and `?page_size=` query parameters. No authentication required.

## CI/CD

The [GitHub Actions workflow](.github/workflows/ci.yml) runs on every push and pull request to `main`:

- **Backend job** — flake8 linting, black formatting check, Django test suite (SQLite)
- **Frontend job** — dependency install (`npm ci`), production build (`npm run build`)
