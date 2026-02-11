from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://bhargavi:bindu@localhost:5432/vistara_analytics"
)