import pandas as pd
from pathlib import Path
from database_connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "faers_drug_adverse_events.csv"


def load_csv_to_database():
    print("Reading CSV file...")

    df = pd.read_csv(RAW_DATA_PATH)

    print("CSV loaded successfully.")
    print("Shape:", df.shape)

    engine = get_engine()

    print("Saving data to SQLite database...")

    df.to_sql(
        "adverse_events",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Data saved to database successfully.")
    print("Table name: adverse_events")


if __name__ == "__main__":
    load_csv_to_database()
