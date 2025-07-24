import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# google cloud sql connector for secure connections
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

# Environment variables for Cloud SQL
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")  # "project:region:instance"

# Optional settings for local development
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 5432))

connector = Connector()


def getconn():
    """Create a new database connection using the Cloud SQL Python Connector.

    Falls back to a TCP connection when INSTANCE_CONNECTION_NAME is not set
    (useful for local development). Any failure raises RuntimeError so the
    calling code can handle database errors gracefully.
    """
    try:
        if INSTANCE_CONNECTION_NAME:
            # Connect via the Cloud SQL Python Connector using pg8000 driver
            conn = connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
                ip_type=IPTypes.PUBLIC,
            )
            return conn
        # Fallback to standard TCP connection for local usage
        return pg8000.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to connect to database: {exc}") from exc


# SQLAlchemy engine with connection pooling
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_pre_ping=True,  # validate connections
    pool_size=5,
    max_overflow=2,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Provide a session to path operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
