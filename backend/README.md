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
