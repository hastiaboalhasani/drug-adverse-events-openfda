# Database Schema Documentation

## Project Title

Adverse Drug Event Analysis and Serious Event Prediction using FDA FAERS Data

## Database

SQLite database: `database/faers.db`

## Tables

### 1. reports

Central table containing one row per adverse event report.

| Column | Description |
|---|---|
| report_id | Unique safety report identifier |
| query_drug | Drug keyword used for collecting the report |
| serious | Binary target variable: 1 = serious, 0 = non-serious |
| report_date | Date when the event was received |
| receipt_date | Date when the report was received |
| country | Country where the event occurred |
| num_drugs | Number of drugs mentioned in the report |
| num_suspect_drugs | Number of suspect drugs in the report |
| num_reactions | Number of adverse reactions in the report |

### 2. patients

Contains patient-level information for each report.

| Column | Description |
|---|---|
| patient_id | Unique patient row identifier |
| report_id | Foreign key linking to reports.report_id |
| patient_age | Patient age |
| patient_age_unit | Unit of patient age |
| patient_sex | Patient sex |
| patient_weight | Patient weight |

### 3. drugs

Contains drug-level information. Each report can include multiple drugs.

| Column | Description |
|---|---|
| drug_id | Unique drug row identifier |
| report_id | Foreign key linking to reports.report_id |
| drug_name | Name of the drug |
| is_suspect | Whether the drug was marked as suspect |
| administration_route | Drug administration route |

### 4. reactions

Contains adverse reaction information. Each report can include multiple reactions.

| Column | Description |
|---|---|
| reaction_id | Unique reaction row identifier |
| report_id | Foreign key linking to reports.report_id |
| reaction_name | MedDRA preferred term for adverse reaction |
| reaction_outcome | Reported outcome of the reaction |

## Relationships

- `reports.report_id` → `patients.report_id`
- `reports.report_id` → `drugs.report_id`
- `reports.report_id` → `reactions.report_id`

Each report has one patient record, multiple drug records, and multiple reaction records.
