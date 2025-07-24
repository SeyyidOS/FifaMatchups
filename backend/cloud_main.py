"""Example FastAPI app for Google Cloud Run using Cloud SQL Postgres."""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .cloud_db import Base, engine, get_db
from .cloud_models import NameEntry

app = FastAPI(title="Cloud Run Sample")


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on service startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_names(db: Session = Depends(get_db)):
    """Return all stored names."""
    try:
        return db.query(NameEntry).all()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/add/{name}")
def add_name(name: str, db: Session = Depends(get_db)):
    """Insert a new row into the NameEntry table."""
    try:
        entry = NameEntry(name=name)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
