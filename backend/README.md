# Backend API

This folder contains a simple FastAPI backend for the FIFA Matchup Generator.

## Setup

Install the Python dependencies:

```bash
pip install -r backend/requirements.txt
```

Run the development server:

```bash
uvicorn backend.main:app --reload
```

The API will start on `http://127.0.0.1:8000` with interactive docs available at `/docs`.

## Admin actions

Two additional endpoints allow administrators to remove players and matches from the database:

```http
DELETE /players/{player_id}
DELETE /matches/{match_id}
```

Requests to these endpoints must include an `X-Admin-Token` header matching the token configured in `backend/main.py` (default is `secret`).
