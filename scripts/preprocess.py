import pandas as pd
from database_connection import get_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def load_data():

    engine = get_engine()

    query = """
    SELECT
        r.report_id,
        r.serious,
        r.num_drugs,
        r.num_suspect_drugs,
        r.num_reactions,
        p.patient_age,
        p.patient_sex,
        p.patient_weight
    FROM reports r
    LEFT JOIN patients p
    ON r.report_id = p.report_id
    """

    df = pd.read_sql(query, engine)

    return df


def clean_data(df):

   
    df["patient_age"] = df["patient_age"].fillna(df["patient_age"].median())
    df["patient_weight"] = df["patient_weight"].fillna(df["patient_weight"].median())

    df["patient_sex"] = df["patient_sex"].fillna("unknown")

    return df


def encode_features(df):

    df = pd.get_dummies(
        df,
        columns=["patient_sex"],
        drop_first=True
    )

    return df


def save_dataset(df):

    output_path = BASE_DIR / "data" / "processed" / "model_dataset.csv"

    df.to_csv(output_path, index=False)

    print("Dataset saved to:")
    print(output_path)

    print("Dataset shape:", df.shape)


def main():

    print("Loading data from database...")
    df = load_data()

    print("Initial shape:", df.shape)

    df = clean_data(df)

    df = encode_features(df)

    save_dataset(df)


if __name__ == "__main__":
    main()
