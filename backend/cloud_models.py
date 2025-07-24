from sqlalchemy import Column, Integer, String
from .cloud_db import Base


class NameEntry(Base):
    """Simple table storing names."""

    __tablename__ = "name_entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
