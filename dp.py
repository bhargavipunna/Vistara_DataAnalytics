from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://bhargavi:bindu@localhost:5432/vistara_analytics"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
