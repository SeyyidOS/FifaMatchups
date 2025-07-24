from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Allow overriding the database connection string via the ``DATABASE_URL``
# environment variable. This prevents accidentally using the fallback value
# (which previously pointed to a local SQLite file) when deploying the
# application.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@104.154.59.245:5432/matchups_db",
)

# ``pool_pre_ping=True`` avoids issues with dropped connections on platforms
# where the database might close idle connections.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
