from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse

password = urllib.parse.quote_plus("FifaMatchups.23")

DATABASE_URL = (
    f"postgresql+psycopg2://postgres:postgres@104.154.59.245:5432/matchups_db"
)

engine = create_engine(DATABASE_URL)  # ← No connect_args here
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
