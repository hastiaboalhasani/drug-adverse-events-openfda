import requests
import pandas as pd
from tqdm import tqdm
import time


DRUGS = [
    "metformin","insulin","glipizide","sitagliptin","empagliflozin",
    "ibuprofen","aspirin","naproxen","acetaminophen","diclofenac",
    "amoxicillin","azithromycin","ciprofloxacin","doxycycline","cephalexin"
]

START_DATE = "20190101"
END_DATE = "20251231"

BASE_URL = "https://api.fda.gov/drug/event.json"

LIMIT = 100
MAX_RECORDS_PER_DRUG = 1000

rows = []


def fetch_drug_events(drug):

    skip = 0
    collected = 0

    while collected < MAX_RECORDS_PER_DRUG:

        params = {
            "search": f'patient.drug.medicinalproduct:"{drug}" AND receivedate:[{START_DATE} TO {END_DATE}]',
            "limit": LIMIT,
            "skip": skip
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=30)

            if response.status_code != 200:
                print(f"API error for {drug}")
                break

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for item in results:

                report_id = item.get("safetyreportid")
                serious = item.get("serious")
                receivedate = item.get("receivedate")
                receiptdate = item.get("receiptdate")
                occurcountry = item.get("occurcountry")

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
                    name = r.get("reactionmeddrapt")
                    outcome = r.get("reactionoutcome")

                    if name:
                        reaction_names.append(name)

                    if outcome:
                        reaction_outcomes.append(str(outcome))

                all_drugs = []
                suspect_drugs = []
                routes = []

                for d in drugs:

                    drug_name = d.get("medicinalproduct")
                    role = d.get("drugcharacterization")
                    route = d.get("drugadministrationroute")

                    if drug_name:
                        all_drugs.append(drug_name)

                    if route:
                        routes.append(str(route))

                    if role == "1" and drug_name:
                        suspect_drugs.append(drug_name)

                row = {
                    "report_id": report_id,
                    "query_drug": drug,
                    "serious": serious,
                    "report_date": receivedate,
                    "receipt_date": receiptdate,
                    "country": occurcountry,

                    "patient_age": patient_age,
                    "patient_age_unit": patient_age_unit,
                    "patient_sex": patient_sex,
                    "patient_weight": patient_weight,

                    "all_drugs": "; ".join(all_drugs),
                    "suspect_drugs": "; ".join(suspect_drugs),
                    "reactions": "; ".join(reaction_names),
                    "reaction_outcomes": "; ".join(reaction_outcomes),
                    "administration_routes": "; ".join(routes),

                    "num_drugs": len(all_drugs),
                    "num_suspect_drugs": len(suspect_drugs),
                    "num_reactions": len(reaction_names),
                }

                rows.append(row)

            collected += len(results)
            skip += LIMIT

            time.sleep(0.3)

        except Exception as e:
            print(f"Error collecting {drug}: {e}")
            break


for drug in tqdm(DRUGS):

    fetch_drug_events(drug)


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

    df = df.drop_duplicates(subset=["report_id"])


df.to_csv("faers_drug_adverse_events.csv", index=False)

print("Dataset saved")
print("Shape:", df.shape)
print(df.head())
