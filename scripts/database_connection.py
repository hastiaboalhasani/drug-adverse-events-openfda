from sqlalchemy import create_engine
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database" / "faers.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")


def get_engine():
    return engine
