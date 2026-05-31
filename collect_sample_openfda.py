import requests
import pandas as pd
from tqdm import tqdm
import time


DRUGS = [
    # Diabetes medications
    "metformin",
    "insulin",
    "glipizide",
    "sitagliptin",
    "empagliflozin",

    # Painkillers / anti-inflammatory drugs
    "ibuprofen",
    "aspirin",
    "naproxen",
    "acetaminophen",
    "diclofenac",

    # Antibiotics
    "amoxicillin",
    "azithromycin",
    "ciprofloxacin",
    "doxycycline",
    "cephalexin"
]

START_DATE = "20190101"
END_DATE = "20251231"

BASE_URL = "https://api.fda.gov/drug/event.json"

LIMIT_PER_DRUG = 100  

rows = []


def safe_get(d, path, default=None):
    """
    Helper function for safe nested dictionary access.
    path example: ["patient", "patientsex"]
    """
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


for query_drug in tqdm(DRUGS, desc="Collecting drug adverse event reports"):
    params = {
        "search": f'patient.drug.medicinalproduct:"{query_drug}" AND receivedate:[{START_DATE} TO {END_DATE}]',
        "limit": LIMIT_PER_DRUG
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)

        if response.status_code != 200:
            print(f"Failed for {query_drug}: {response.status_code}")
            print(response.text[:300])
            continue

        data = response.json()
        results = data.get("results", [])

        for item in results:
            report_id = item.get("safetyreportid")
            serious = item.get("serious")
            receivedate = item.get("receivedate")
            receiptdate = item.get("receiptdate")
            occurcountry = item.get("occurcountry")
            companynumb = item.get("companynumb")

            patient = item.get("patient", {})

            patient_age = patient.get("patientonsetage")
            patient_age_unit = patient.get("patientonsetageunit")
            patient_sex = patient.get("patientsex")
            patient_weight = patient.get("patientweight")

            reactions = patient.get("reaction", [])
            drugs = patient.get("drug", [])

            reaction_names = []
            reaction_outcomes = []

            for r in reactions:
                reaction_name = r.get("reactionmeddrapt")
                reaction_outcome = r.get("reactionoutcome")

                if reaction_name:
                    reaction_names.append(reaction_name)

                if reaction_outcome:
                    reaction_outcomes.append(str(reaction_outcome))

            all_drug_names = []
            suspect_drug_names = []
            drug_roles = []
            routes = []

            for d in drugs:
                drug_name = d.get("medicinalproduct")
                drug_role = d.get("drugcharacterization")
                route = d.get("drugadministrationroute")

                if drug_name:
                    all_drug_names.append(drug_name)

                if drug_role:
                    drug_roles.append(str(drug_role))

                if route:
                    routes.append(str(route))

                # In FAERS, drugcharacterization:
                # 1 = suspect
                # 2 = concomitant
                # 3 = interacting
                if drug_role == "1" and drug_name:
                    suspect_drug_names.append(drug_name)

            row = {
                "report_id": report_id,
                "query_drug": query_drug,
                "serious": serious,
                "report_date": receivedate,
                "receipt_date": receiptdate,
                "country": occurcountry,
                "company_number": companynumb,

                "patient_age": patient_age,
                "patient_age_unit": patient_age_unit,
                "patient_sex": patient_sex,
                "patient_weight": patient_weight,

                "all_drugs": "; ".join(all_drug_names),
                "suspect_drugs": "; ".join(suspect_drug_names),
                "reactions": "; ".join(reaction_names),
                "reaction_outcomes": "; ".join(reaction_outcomes),
                "drug_roles": "; ".join(drug_roles),
                "administration_routes": "; ".join(routes),

                "num_drugs": len(all_drug_names),
                "num_suspect_drugs": len(suspect_drug_names),
                "num_reactions": len(reaction_names),
            }

            rows.append(row)

        time.sleep(0.3)

    except Exception as e:
        print(f"Error for {query_drug}: {e}")


df = pd.DataFrame(rows)


if not df.empty:
    df["serious"] = df["serious"].replace({
        "1": 1,
        "2": 0
    })

    df["patient_sex"] = df["patient_sex"].replace({
        "1": "male",
        "2": "female",
        "0": "unknown"
    })


    df["report_date"] = pd.to_datetime(df["report_date"], format="%Y%m%d", errors="coerce")
    df["receipt_date"] = pd.to_datetime(df["receipt_date"], format="%Y%m%d", errors="coerce")

    df = df.drop_duplicates(subset=["report_id", "query_drug"])

output_file = "sample_openfda_adverse_events.csv"
df.to_csv(output_file, index=False)

print("Done.")
print(f"Saved file: {output_file}")
print("Shape:", df.shape)
print(df.head())
