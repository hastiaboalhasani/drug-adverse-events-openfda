import subprocess

print("Step 1: Loading data from database...")
subprocess.run(["python", "scripts/load_data.py"])

print("Step 2: Preprocessing data...")
subprocess.run(["python", "scripts/preprocess.py"])

print("Step 3: Feature engineering...")
subprocess.run(["python", "scripts/feature_engineering.py"])

print("Step 4: Building interaction network...")
subprocess.run(["python", "scripts/interaction_network.py"])

print("Step 5: Calculating graph-based risk scores...")
subprocess.run(["python", "scripts/graph_risk_scoring.py"])

print("Step 6: Training machine learning model...")
subprocess.run(["python", "scripts/train_model.py"])

print("Pipeline finished successfully.")
