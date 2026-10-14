from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from app.core.config import settings

db_url = settings.DATABASE_URL
# Handle postgres prefix fix if needed (e.g. postgres:// to postgresql://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30  # 30s wait timeout for concurrent writes
    engine_kwargs["connect_args"] = connect_args
    # Use StaticPool only for in-memory, otherwise use default pool
    if ":memory:" in db_url:
        engine_kwargs["poolclass"] = StaticPool
else:
    # Production PostgreSQL connection pool configuration
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = 25
    engine_kwargs["max_overflow"] = 15
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_timeout"] = 30

engine = create_engine(db_url, **engine_kwargs)

# For SQLite, enable Write-Ahead Logging (WAL) and busy timeout for high concurrency
if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=10000;")  # 10s busy wait
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> bool:
    """Verifies that the database connection pool is healthy and accepting queries."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
