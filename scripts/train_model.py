import json
import sqlite3
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "processed" / "model_dataset.csv"
RISK_PATH = BASE_DIR / "data" / "processed" / "graph_based_drug_risks.csv"

DB_PATH_OPTIONS = [
    BASE_DIR / "database" / "faers.db",
    BASE_DIR / "data" / "drug_adverse_events.db",
    BASE_DIR / "data" / "faers.db",
    BASE_DIR / "data" / "openfda.db",
    BASE_DIR / "database.db",
    BASE_DIR / "openfda.db",
]

ARTIFACTS_DIR = BASE_DIR / "models"
FIGURES_DIR = BASE_DIR / "reports" / "figures"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def find_database_path():
    for path in DB_PATH_OPTIONS:
        if path.exists():
            return path

    print("Could not find SQLite database.")
    print("Checked paths:")
    for path in DB_PATH_OPTIONS:
        print(path)

    return None


def normalize_drug_name(value):
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def detect_column(columns, candidates):
    for col in candidates:
        if col in columns:
            return col
    return None


def load_drug_table(db_path):
    conn = sqlite3.connect(db_path)

    cols_df = pd.read_sql_query("PRAGMA table_info(drugs);", conn)
    drug_columns = cols_df["name"].tolist()

    if "report_id" not in drug_columns:
        conn.close()
        raise ValueError("drugs table does not contain report_id column.")

    drug_name_col = detect_column(
        drug_columns,
        [
            "medicinalproduct",
            "drug_name",
            "drugname",
            "drug",
            "name",
            "product_name",
            "generic_name",
        ],
    )

    if drug_name_col is None:
        conn.close()
        raise ValueError(f"Could not detect drug name column. Columns: {drug_columns}")

    query = f"""
        SELECT report_id, {drug_name_col} AS drug_name
        FROM drugs
        WHERE {drug_name_col} IS NOT NULL
    """

    drugs_df = pd.read_sql_query(query, conn)
    conn.close()

    drugs_df["drug_name"] = drugs_df["drug_name"].apply(normalize_drug_name)

    print(f"Using drug name column: {drug_name_col}")

    return drugs_df


def save_outputs(
    model,
    importances,
    cm,
    y_test,
    y_pred,
    y_prob,
    roc_auc,
    features,
    y_train,
):
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    model_path = ARTIFACTS_DIR / "random_forest_graph_risk_model.pkl"
    joblib.dump(model, model_path)

    feature_importance_path = PROCESSED_DIR / "feature_importances.csv"
    importances.to_csv(feature_importance_path, index=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=importances,
        x="importance",
        y="feature",
        hue="feature",
        palette="viridis",
        legend=False,
    )
    plt.title("Random Forest Feature Importances")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_importances.png", dpi=300)
    plt.close()

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Predicted Non-serious", "Predicted Serious"],
        yticklabels=["Actual Non-serious", "Actual Serious"],
    )
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=300)
    plt.close()

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc_value = auc(fpr, tpr)

    plt.figure(figsize=(7, 6))
    plt.plot(
        fpr,
        tpr,
        color="darkorange",
        lw=2,
        label=f"ROC Curve AUC = {roc_auc_value:.4f}",
    )
    plt.plot(
        [0, 1],
        [0, 1],
        color="navy",
        lw=2,
        linestyle="--",
        label="Random Baseline",
    )
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "roc_curve.png", dpi=300)
    plt.close()

    metrics = {
        "model": "RandomForestClassifier",
        "roc_auc": float(roc_auc),
        "accuracy": float((y_pred == y_test).mean()),
        "features": features,
        "confusion_matrix": cm.tolist(),
        "class_distribution_training": {
            str(k): float(v)
            for k, v in y_train.value_counts(normalize=True).to_dict().items()
        },
    }

    metrics_path = PROCESSED_DIR / "model_metrics.json"

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"Model saved: {model_path}")
    print(f"Feature importances saved: {feature_importance_path}")
    print(f"Metrics saved: {metrics_path}")
    print(f"Figures saved: {FIGURES_DIR}")


def main():
    print("Starting machine learning pipeline")

    if not DATA_PATH.exists():
        print(f"Model dataset not found: {DATA_PATH}")
        return

    if not RISK_PATH.exists():
        print(f"Graph risk file not found: {RISK_PATH}")
        return

    db_path = find_database_path()

    if db_path is None:
        return

    print(f"Using database: {db_path}")

    df = pd.read_csv(DATA_PATH)
    risk_df = pd.read_csv(RISK_PATH)

    print("Model dataset columns:")
    print(df.columns.tolist())

    print("Graph risk file columns:")
    print(risk_df.columns.tolist())

    risk_drug_col = detect_column(
        risk_df.columns,
        [
            "drug_name",
            "drug",
            "medicinalproduct",
            "name",
        ],
    )

    risk_score_col = detect_column(
        risk_df.columns,
        [
            "normalized_risk_score",
            "graph_based_risk_score",
            "risk_score",
            "pagerank_score",
            "score",
        ],
    )

    if risk_drug_col is None:
        print("Could not detect drug name column in graph risk file.")
        return

    if risk_score_col is None:
        print("Could not detect risk score column in graph risk file.")
        return

    print(f"Using graph risk columns: {risk_drug_col}, {risk_score_col}")

    risk_df["drug_name_norm"] = risk_df[risk_drug_col].apply(normalize_drug_name)

    risk_map = dict(
        zip(
            risk_df["drug_name_norm"],
            risk_df[risk_score_col].fillna(0),
        )
    )

    drugs_df = load_drug_table(db_path)

    drugs_df["drug_graph_risk"] = drugs_df["drug_name"].map(risk_map).fillna(0)

    nonzero_count = int((drugs_df["drug_graph_risk"] > 0).sum())
    total_count = len(drugs_df)

    print(f"Non-zero drug risk matches: {nonzero_count} / {total_count}")

    if nonzero_count == 0:
        print("No drugs matched graph risk scores.")
        print("Example database drug names:")
        print(drugs_df["drug_name"].dropna().unique()[:20])
        print("Example graph risk drug names:")
        print(risk_df["drug_name_norm"].dropna().unique()[:20])
        return

    report_risk_df = (
        drugs_df.groupby("report_id")
        .agg(
            max_drug_risk=("drug_graph_risk", "max"),
            avg_drug_risk=("drug_graph_risk", "mean"),
            sum_drug_risk=("drug_graph_risk", "sum"),
        )
        .reset_index()
    )

    df = df.merge(report_risk_df, on="report_id", how="left")

    df["max_drug_risk"] = df["max_drug_risk"].fillna(0)
    df["avg_drug_risk"] = df["avg_drug_risk"].fillna(0)
    df["sum_drug_risk"] = df["sum_drug_risk"].fillna(0)

    candidate_features = [
        "patient_age",
        "patient_weight",
        "num_drugs",
        "num_suspect_drugs",
        "num_reactions",
        "patient_sex_male",
        "patient_sex_unknown",
        "max_drug_risk",
        "avg_drug_risk",
        "sum_drug_risk",
    ]

    features = [col for col in candidate_features if col in df.columns]

    print("Features used:")
    print(features)

    X = df[features].fillna(0)
    y = df["serious"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Training class distribution:")
    print(y_train.value_counts(normalize=True))

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("Model evaluation:")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)

    print("Confusion Matrix:")
    print(cm)

    roc_auc = roc_auc_score(y_test, y_prob)

    print(f"ROC-AUC Score: {roc_auc:.4f}")

    importances = (
        pd.DataFrame(
            {
                "feature": features,
                "importance": model.feature_importances_,
            }
        )
        .sort_values(by="importance", ascending=False)
        .reset_index(drop=True)
    )

    print("Feature Importances:")
    print(importances)

    output_path = PROCESSED_DIR / "model_dataset_with_graph_risk.csv"
    df.to_csv(output_path, index=False)

    print(f"Enhanced dataset saved: {output_path}")

    save_outputs(
        model=model,
        importances=importances,
        cm=cm,
        y_test=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        roc_auc=roc_auc,
        features=features,
        y_train=y_train,
    )


if __name__ == "__main__":
    main()
