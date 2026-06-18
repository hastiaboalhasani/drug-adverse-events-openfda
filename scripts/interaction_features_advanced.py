import pandas as pd
from itertools import combinations
from pathlib import Path
import re
from database_connection import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]

MIN_REPORTS = 20


BRAND_TO_GENERIC = {
    "NEXIUM": "ESOMEPRAZOLE",
    "NEXIUM 24HR": "ESOMEPRAZOLE",
    "PRILOSEC": "OMEPRAZOLE",
    "PRILOSEC OTC": "OMEPRAZOLE",
    "PREVACID": "LANSOPRAZOLE",
    "PREVACID 24 HR": "LANSOPRAZOLE",
    "PROTONIX": "PANTOPRAZOLE",
    "TYLENOL": "ACETAMINOPHEN",
    "ADVIL": "IBUPROFEN",
    "MOTRIN": "IBUPROFEN",
    "ALEVE": "NAPROXEN",
    "GLUCOPHAGE": "METFORMIN",
    "ZITHROMAX": "AZITHROMYCIN",
    "CIPRO": "CIPROFLOXACIN",
}


def clean_drug_name(name):
    if pd.isna(name):
        return None

    name = str(name).upper().strip()

    # remove trailing dots
    name = re.sub(r"\.+$", "", name)

    # normalize spaces
    name = re.sub(r"\s+", " ", name)

    # map brands to generics
    name = BRAND_TO_GENERIC.get(name, name)

    return name


def load_data():
    engine = get_engine()

    drugs = pd.read_sql(
        """
        SELECT report_id, drug_name, is_suspect
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


def generate_suspect_drug_pairs(drugs):
    """
    Generate unique suspect drug pairs per report.
    """

    suspect_drugs = drugs[drugs["is_suspect"] == 1].copy()

    pairs = []

    for report_id, group in suspect_drugs.groupby("report_id"):

        drug_list = sorted(set(group["drug_name"]))

        if len(drug_list) < 2:
            continue

        for drug_a, drug_b in combinations(drug_list, 2):

            
            if drug_a == drug_b:
                continue

            pairs.append({
                "report_id": report_id,
                "drug_a": drug_a,
                "drug_b": drug_b
            })

    return pd.DataFrame(pairs)


def compute_pair_statistics(pair_df, reports):
   

    pair_df = pair_df.merge(reports, on="report_id", how="left")

    total_reports = reports["report_id"].nunique()
    total_serious = reports["serious"].sum()
    total_non_serious = total_reports - total_serious

    report_level_serious_rate = total_serious / total_reports

    stats = pair_df.groupby(["drug_a", "drug_b"]).agg(
        total_pair_reports=("report_id", "nunique"),
        serious_pair_reports=("serious", "sum")
    ).reset_index()

    stats["non_serious_pair_reports"] = (
        stats["total_pair_reports"] - stats["serious_pair_reports"]
    )

    stats["serious_rate"] = (
        stats["serious_pair_reports"] / stats["total_pair_reports"]
    )

    stats["lift_vs_report_baseline"] = (
        stats["serious_rate"] / report_level_serious_rate
    )


    stats["a"] = stats["serious_pair_reports"]
    stats["b"] = stats["non_serious_pair_reports"]
    stats["c"] = total_serious - stats["a"]
    stats["d"] = total_non_serious - stats["b"]

   
    stats["odds_ratio"] = (
        ((stats["a"] + 0.5) * (stats["d"] + 0.5)) /
        ((stats["b"] + 0.5) * (stats["c"] + 0.5))
    )


    stats["risk_score"] = (
        stats["lift_vs_report_baseline"]
        * stats["odds_ratio"]
        * stats["total_pair_reports"]
    )

    reliable = stats[stats["total_pair_reports"] >= MIN_REPORTS].copy()

    reliable = reliable.sort_values(
        by=["risk_score", "odds_ratio", "lift_vs_report_baseline"],
        ascending=False
    )

    return stats, reliable, report_level_serious_rate


def save_results(all_stats, reliable_stats):
    output_all = BASE_DIR / "data" / "processed" / "suspect_drug_interactions_all.csv"
    output_reliable = BASE_DIR / "data" / "processed" / "suspect_drug_interactions_reliable.csv"

    all_stats.to_csv(output_all, index=False)
    reliable_stats.to_csv(output_reliable, index=False)

    print("Saved all suspect drug interactions:")
    print(output_all)

    print("\nSaved reliable suspect drug interactions:")
    print(output_reliable)


def main():
    print("Loading data...")
    drugs, reports = load_data()

    print("Generating suspect drug pairs...")
    pair_df = generate_suspect_drug_pairs(drugs)

    print("Number of suspect drug pair rows:", len(pair_df))

    if pair_df.empty:
        print("No suspect drug pairs found. Check is_suspect values in drugs table.")
        return

    print("Computing advanced interaction statistics...")
    all_stats, reliable_stats, baseline_rate = compute_pair_statistics(pair_df, reports)

    save_results(all_stats, reliable_stats)

    print("\nReport-level baseline serious rate:")
    print(round(baseline_rate, 4))

    print("\nNumber of unique suspect drug pairs:")
    print(len(all_stats))

    print(f"\nNumber of reliable suspect drug pairs with total_pair_reports >= {MIN_REPORTS}:")
    print(len(reliable_stats))

    print("\nTop 20 reliable high-risk suspect drug combinations:\n")
    print(
        reliable_stats[
            [
                "drug_a",
                "drug_b",
                "total_pair_reports",
                "serious_pair_reports",
                "serious_rate",
                "lift_vs_report_baseline",
                "odds_ratio",
                "risk_score"
            ]
        ].head(20)
    )


if __name__ == "__main__":
    main()
