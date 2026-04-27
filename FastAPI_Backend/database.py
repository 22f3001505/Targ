"""
TARG - Database Setup
SQLAlchemy database setup for persistent user data.

Local default: SQLite.
Production/Render: PostgreSQL via DATABASE_URL.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./targ.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: yields a DB session per request, auto-closes after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables on startup."""
    Base.metadata.create_all(bind=engine)
    ensure_schema()


def ensure_schema():
    """Add columns that older Render databases may be missing.

    SQLAlchemy create_all creates absent tables, but it does not migrate
    existing tables. Keep this small and idempotent for Render free-tier deploys.
    """
    inspector = inspect(engine)
    table_columns = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in inspector.get_table_names()
    }

    def add_column(table: str, column: str, definition: str) -> None:
        if column in table_columns.get(table, set()):
            return
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        table_columns.setdefault(table, set()).add(column)

    add_column("users", "full_name", "VARCHAR(200)")
    add_column("users", "created_at", "TIMESTAMP")
    add_column("users", "updated_at", "TIMESTAMP")

    add_column("saved_meals", "fiber", "FLOAT")
    add_column("saved_meals", "recipe_data", "JSON")

    add_column("workout_logs", "duration_minutes", "INTEGER")
    add_column("workout_logs", "calories_burned", "INTEGER")
    add_column("workout_logs", "notes", "TEXT")

    add_column("meal_plans", "week_start", "VARCHAR(20)")
