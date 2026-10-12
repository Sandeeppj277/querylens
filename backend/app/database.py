"""
Database connection layer — SQLAlchemy engine + session management.
"""

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL, DB_PATH

# Ensure the data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine (check_same_thread=False is needed for SQLite + FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enable foreign keys for SQLite (off by default)
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_schema_info() -> str:
    """
    Introspect the database and return a formatted string of all tables,
    columns, and types. This is sent to the LLM so it knows the schema.
    """
    with engine.connect() as conn:
        # Get all table names
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        ).fetchall()

        schema_parts = []
        for (table_name,) in tables:
            # Get column info for each table
            columns = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
            col_defs = []
            for col in columns:
                # col: (cid, name, type, notnull, dflt_value, pk)
                col_str = f"    {col[1]} {col[2]}"
                if col[5]:  # primary key
                    col_str += " PRIMARY KEY"
                if col[3]:  # not null
                    col_str += " NOT NULL"
                col_defs.append(col_str)

            # Get foreign key info
            fks = conn.execute(text(f"PRAGMA foreign_key_list('{table_name}')")).fetchall()
            fk_defs = []
            for fk in fks:
                # fk: (id, seq, table, from, to, on_update, on_delete, match)
                fk_defs.append(f"    FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})")

            all_defs = col_defs + fk_defs
            schema_parts.append(
                f"CREATE TABLE {table_name} (\n" + ",\n".join(all_defs) + "\n);"
            )

        return "\n\n".join(schema_parts)
