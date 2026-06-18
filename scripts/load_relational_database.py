import pandas as pd
from pathlib import Path
from database_connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "faers_drug_adverse_events.csv"


def split_semicolon_values(value):
  
    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip() != ""
    ]


def create_reports_table(df):
    reports_cols = [
        "report_id",
        "query_drug",
        "serious",
        "report_date",
        "receipt_date",
        "country",
        "num_drugs",
        "num_suspect_drugs",
        "num_reactions"
    ]

    reports_df = df[reports_cols].copy()

    reports_df = reports_df.drop_duplicates(subset=["report_id"])

    return reports_df


def create_patients_table(df):
    patients_cols = [
        "report_id",
        "patient_age",
        "patient_age_unit",
        "patient_sex",
        "patient_weight"
    ]

    patients_df = df[patients_cols].copy()

    patients_df = patients_df.drop_duplicates(subset=["report_id"])
    patients_df.insert(0, "patient_id", range(1, len(patients_df) + 1))

    return patients_df


def create_drugs_table(df):
    drug_rows = []

    for _, row in df.iterrows():
        report_id = row["report_id"]

        all_drugs = split_semicolon_values(row.get("all_drugs"))
        suspect_drugs = split_semicolon_values(row.get("suspect_drugs"))
        routes = split_semicolon_values(row.get("administration_routes"))

        suspect_set = set([drug.lower() for drug in suspect_drugs])

        for i, drug_name in enumerate(all_drugs):
            route = routes[i] if i < len(routes) else None

            is_suspect = 1 if drug_name.lower() in suspect_set else 0

            drug_rows.append({
                "report_id": report_id,
                "drug_name": drug_name,
                "is_suspect": is_suspect,
                "administration_route": route
            })

    drugs_df = pd.DataFrame(drug_rows)

    if not drugs_df.empty:
        drugs_df.insert(0, "drug_id", range(1, len(drugs_df) + 1))

    return drugs_df


def create_reactions_table(df):
    reaction_rows = []

    for _, row in df.iterrows():
        report_id = row["report_id"]

        reactions = split_semicolon_values(row.get("reactions"))
        outcomes = split_semicolon_values(row.get("reaction_outcomes"))

        for i, reaction_name in enumerate(reactions):
            outcome = outcomes[i] if i < len(outcomes) else None

            reaction_rows.append({
                "report_id": report_id,
                "reaction_name": reaction_name,
                "reaction_outcome": outcome
            })

    reactions_df = pd.DataFrame(reaction_rows)

    if not reactions_df.empty:
        reactions_df.insert(0, "reaction_id", range(1, len(reactions_df) + 1))

    return reactions_df


def load_relational_database():
    print("Reading raw CSV file...")

    df = pd.read_csv(RAW_DATA_PATH)

    print("Raw data loaded.")
    print("Raw shape:", df.shape)

    print("Creating reports table...")
    reports_df = create_reports_table(df)
    print("Reports shape:", reports_df.shape)

    print("Creating patients table...")
    patients_df = create_patients_table(df)
    print("Patients shape:", patients_df.shape)

    print("Creating drugs table...")
    drugs_df = create_drugs_table(df)
    print("Drugs shape:", drugs_df.shape)

    print("Creating reactions table...")
    reactions_df = create_reactions_table(df)
    print("Reactions shape:", reactions_df.shape)

    engine = get_engine()

    print("Saving tables to SQLite database...")

    reports_df.to_sql("reports", con=engine, if_exists="replace", index=False)
    patients_df.to_sql("patients", con=engine, if_exists="replace", index=False)
    drugs_df.to_sql("drugs", con=engine, if_exists="replace", index=False)
    reactions_df.to_sql("reactions", con=engine, if_exists="replace", index=False)

    print("Relational database created successfully.")
    print("Database path:", BASE_DIR / "database" / "faers.db")


if __name__ == "__main__":
    load_relational_database()
