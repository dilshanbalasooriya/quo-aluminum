import os
from sqlmodel import SQLModel, Session, create_engine

# Defaulting to SQLite for local development; override with your production DB URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aluminium_quotation.db")

# check_same_thread is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# The engine is the core interface to the database
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


class DatabaseManager:
    """Manages database connection and session creation."""

    @classmethod
    def create_db_and_tables(cls):
        """Creates all tables defined in your SQLModel classes."""
        # Note: Ensure all your SQLModel classes are imported before calling this
        SQLModel.metadata.create_all(engine)

    @classmethod
    def get_session(cls):
        """
        Yields a database session. 
        Can be used as a FastAPI dependency or a standard context manager.
        """
        with Session(engine) as session:
            yield session