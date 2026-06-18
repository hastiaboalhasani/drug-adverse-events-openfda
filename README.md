# Drug Adverse Event Analysis using openFDA FAERS

This project analyzes adverse drug event reports using data from the openFDA FAERS database.  
The goal is to explore drug safety patterns, identify important drug-reaction relationships, build a drug interaction network, and predict whether an adverse event report is serious using machine learning.

## Data Source

The dataset was collected from the openFDA Drug Adverse Event API:

https://open.fda.gov/apis/drug/event/

FAERS, the FDA Adverse Event Reporting System, contains reports of adverse events, medication errors, and product quality complaints submitted to the FDA.

The sample dataset used in this project includes adverse event reports for commonly used medications from categories such as:

* Diabetes medications

* Painkillers and anti-inflammatory drugs

* Antibiotics

* Proton pump inhibitors

* Autoimmune and biologic medications

## Project Objectives

The main objectives of this project are:

* Perform exploratory data analysis of adverse drug event reports

* Analyze drug-reaction patterns

* Build a drug interaction network from reported medication combinations

* Calculate graph-based drug risk scores using network centrality

* Combine patient-level features with graph-based drug risk features

* Train a binary classification model to predict serious adverse event reports

* Evaluate model performance using standard classification metrics

## Repository Structure

drug-adverse-events-openfda/  
│  
├── data/  
│   ├── raw/  
│   │   └── faers\_sample.csv  
│   │  
│   └── processed/  
│       ├── model\_dataset.csv  
│       ├── model\_dataset\_with\_graph\_risk.csv  
│       ├── graph\_based\_drug\_risks.csv  
│       ├── feature\_importances.csv  
│       └── model\_metrics.json  
│  
├── database/  
│   └── faers.db  
│  
├── models/  
│   └── random\_forest\_graph\_risk\_model.pkl  
│  
├── reports/  
│   └── figures/  
│       ├── roc\_curve.png  
│       ├── confusion\_matrix.png  
│       ├── feature\_importances.png  
│       └── drug\_interaction\_network.png  
│  
├── scripts/  
│   ├── load\_data.py  
│   ├── preprocess.py  
│   ├── interaction\_features\_advanced.py  
│   ├── build\_interaction\_network.py  
│   ├── graph\_risk\_scoring.py  
│   └── train\_model.py  
│  
├── pipeline.py  
├── requirements.txt  
└── README.md

## Pipeline Overview

The full project pipeline is automated using pipeline.py.

The pipeline performs the following steps:

1. Load raw FAERS adverse event data from CSV

2. Store the data in a SQLite database

3. Preprocess reports and create a machine learning dataset

4. Engineer drug interaction features

5. Build a drug interaction network

6. Calculate graph-based drug risk scores using PageRank

7. Merge graph risk features with patient-level features

8. Train and evaluate a Random Forest classification model

9. Save the final model, metrics, datasets, and figures

To run the complete pipeline:

python pipeline.py

## Data Processing

The raw data is transformed into a structured dataset for modeling.

The processed dataset includes patient-level and report-level features such as:

* Patient age

* Patient weight

* Patient sex

* Number of drugs in the report

* Number of suspect drugs

* Number of reported reactions

* Serious adverse event label

The binary target variable is:

serious

Where:

* 1 \= serious adverse event report

* 0 \= non-serious adverse event report

## Drug Interaction Network

A drug interaction network was constructed based on co-reported suspect drugs in FAERS reports.

In this graph:

* Nodes represent drugs

* Edges represent co-occurrence or interaction relationships between drugs

* Edge weights represent the strength or frequency of the interaction pattern

Network analysis was performed using networkx.

The interaction network included:

Nodes: 84  
Edges: 268

## Graph-Based Risk Scoring

Graph-based drug risk scores were calculated using the PageRank algorithm.

The goal of this step was to identify drugs that occupy central positions in the interaction network.

A higher graph-based risk score indicates that a drug is more central within the reported interaction network.

The top central drugs identified by the graph-based scoring process included:

| Rank | Drug | Normalized Risk Score |
| ----: | :---- | ----: |
| 1 | METFORMIN | 100.00 |
| 2 | ENBREL | 41.65 |
| 3 | ESOMEPRAZOLE | 40.14 |
| 4 | OMEPRAZOLE | 39.96 |
| 5 | ORENCIA | 39.00 |
| 6 | ACETAMINOPHEN | 38.02 |
| 7 | METHOTREXATE | 33.30 |
| 8 | ACTEMRA | 31.22 |
| 9 | HUMIRA | 28.92 |
| 10 | REMICADE | 28.34 |

These results should be interpreted as network centrality patterns within the FAERS sample, not as direct causal evidence of drug danger.

## Machine Learning Model

A Random Forest classifier was trained to predict whether an adverse event report was serious.

The model used both traditional patient/report-level features and graph-derived drug risk features.

### Features Used

patient\_age  
patient\_weight  
num\_drugs  
num\_suspect\_drugs  
num\_reactions  
patient\_sex\_male  
patient\_sex\_unknown  
max\_drug\_risk  
avg\_drug\_risk  
sum\_drug\_risk

The graph-based features were:

* max\_drug\_risk

* avg\_drug\_risk

* sum\_drug\_risk

These features summarize the graph-based risk scores of drugs associated with each adverse event report.

## Model Performance

The final Random Forest model achieved the following performance:

ROC-AUC Score: 0.8396

Classification report:

              precision    recall  f1-score   support

           0       0.46      0.77      0.58       585  
           1       0.92      0.74      0.82      2023

    accuracy                           0.75      2608  
   macro avg       0.69      0.75      0.70      2608  
weighted avg       0.81      0.75      0.77      2608

Confusion matrix:

\[\[ 448  137\]  
 \[ 522 1501\]\]

The model performs well in identifying serious adverse event reports, with strong precision for the serious class.

## Feature Importance

The most important model features were:

| Rank | Feature | Importance |
| ----: | :---- | ----: |
| 1 | patient\_age | 0.194 |
| 2 | num\_suspect\_drugs | 0.159 |
| 3 | num\_drugs | 0.146 |
| 4 | num\_reactions | 0.112 |
| 5 | sum\_drug\_risk | 0.106 |
| 6 | avg\_drug\_risk | 0.087 |
| 7 | max\_drug\_risk | 0.082 |
| 8 | patient\_weight | 0.063 |
| 9 | patient\_sex\_male | 0.034 |
| 10 | patient\_sex\_unknown | 0.016 |

Graph-derived drug risk features contributed approximately:

27.6%

of the total model feature importance.

This suggests that the structure of the drug interaction network provides meaningful predictive information for adverse event severity classification.

## Key Results

* Built a complete FAERS adverse event analysis pipeline

* Created a SQLite database from raw openFDA data

* Constructed a drug interaction network using reported medication combinations

* Applied PageRank-based graph risk scoring to identify central drugs

* Combined graph-based features with patient-level features

* Trained a Random Forest model for serious adverse event prediction

* Achieved a final ROC-AUC score of 0.8396

* Demonstrated that graph-derived drug features contributed approximately 27.6% of model importance

## How to Install and Run

Clone the repository:

git clone \<your-repository-url\>  
cd drug-adverse-events-openfda

Create and activate a virtual environment (optional but recommended):

python \-m venv venv  
source venv/bin/activate

Install dependencies:

pip install \-r requirements.txt

Run the full pipeline:

python pipeline.py

After running the pipeline, generated outputs will be saved in:

data/processed/  
models/  
reports/figures/

## Requirements

Main Python libraries used in this project include:

* pandas

* numpy

* matplotlib

* seaborn

* scipy

* scikit-learn

* networkx

* sqlalchemy

* joblib

Full dependencies are listed in:

requirements.txt

## Limitations

This project uses a sample of FAERS reports and should not be interpreted as a clinical risk assessment tool.

Important limitations include:

* FAERS is a spontaneous reporting system and may contain reporting bias

* Reports do not prove causality between a drug and an adverse event

* Duplicate or incomplete reports may exist

* Drug exposure rates are not available in the dataset

* The model is intended for exploratory and educational analysis only

## Future Work

Potential improvements include:

* Expanding the dataset using more FAERS records

* Adding time-based analysis of adverse event trends

* Improving duplicate report detection

* Testing additional machine learning models such as XGBoost or Logistic Regression

* Applying hyperparameter tuning

* Using SHAP values for model explainability

* Building an interactive dashboard for adverse event exploration

* Adding CI/CD with GitHub Actions

## Disclaimer

This project is for educational and research purposes only.

The results should not be used for medical decision-making.

Any findings from FAERS data should be validated with clinical expertise and additional data sources.