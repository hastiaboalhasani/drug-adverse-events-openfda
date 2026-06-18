import pandas as pd
from itertools import combinations
from database_connection import get_engine
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[1]

MIN_REPORTS = 20


def clean_drug_name(name):
    
    if pd.isna(name):
        return None

    name = str(name).upper().strip()

   
    name = re.sub(r"\.+$", "", name)
    name = re.sub(r"\s+", " ", name)

    return name


def load_data():
    engine = get_engine()

    drugs = pd.read_sql(
        """
        SELECT report_id, drug_name
        FROM drugs
        WHERE drug_name IS NOT NULL
        """,
        engine
    )

    reports = pd.read_sql(
        """
        SELECT report_id, serious
        FROM reports
        """,
        engine
    )

    drugs["drug_name"] = drugs["drug_name"].apply(clean_drug_name)
    drugs = drugs.dropna(subset=["drug_name"])

    return drugs, reports


def generate_drug_pairs(drugs):
    pairs = []

    grouped = drugs.groupby("report_id")

    for report_id, group in grouped:
        drug_list = sorted(set(group["drug_name"]))

        if len(drug_list) < 2:
            continue

        for drug_a, drug_b in combinations(drug_list, 2):
            pairs.append({
                "report_id": report_id,
                "drug_a": drug_a,
                "drug_b": drug_b
            })

    pair_df = pd.DataFrame(pairs)

    return pair_df


def add_serious_label(pair_df, reports):
    df = pair_df.merge(reports, on="report_id", how="left")
    return df


def compute_interaction_risk(df):
    overall_serious_rate = df["serious"].mean()

    stats = df.groupby(["drug_a", "drug_b"]).agg(
        total_reports=("report_id", "count"),
        serious_reports=("serious", "sum")
    ).reset_index()

    stats["serious_rate"] = stats["serious_reports"] / stats["total_reports"]

    stats["lift"] = stats["serious_rate"] / overall_serious_rate

   
    stats["risk_score"] = stats["serious_rate"] * stats["lift"] * stats["total_reports"]

   
    filtered = stats[stats["total_reports"] >= MIN_REPORTS].copy()

    filtered = filtered.sort_values(
        by=["risk_score", "lift", "serious_rate"],
        ascending=False
    )

    return stats, filtered, overall_serious_rate


def save_results(stats, filtered):
    output_all = BASE_DIR / "data" / "processed" / "drug_interactions_all.csv"
    output_filtered = BASE_DIR / "data" / "processed" / "drug_interactions_filtered.csv"

    stats.to_csv(output_all, index=False)
    filtered.to_csv(output_filtered, index=False)

    print("Saved all interactions:")
    print(output_all)

    print("\nSaved filtered reliable interactions:")
    print(output_filtered)


def main():
    print("Loading data...")
    drugs, reports = load_data()

    print("Generating drug pairs...")
    pairs = generate_drug_pairs(drugs)

    print("Pair count:", len(pairs))

    df = add_serious_label(pairs, reports)

    print("Computing interaction risk...")
    stats, filtered, overall_serious_rate = compute_interaction_risk(df)

    save_results(stats, filtered)

    print("\nOverall serious rate:")
    print(round(overall_serious_rate, 4))

    print("\nNumber of unique drug pairs:")
    print(len(stats))

    print("\nNumber of reliable drug pairs with total_reports >=", MIN_REPORTS)
    print(len(filtered))

    print("\nTop 20 reliable high-risk drug combinations:\n")
    print(filtered.head(20))


if __name__ == "__main__":
    main()
