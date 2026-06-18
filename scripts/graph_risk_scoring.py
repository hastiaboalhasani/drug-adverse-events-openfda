import pandas as pd
import networkx as nx
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "processed" / "suspect_drug_interactions_reliable.csv"

def main():
    print("Loading reliable interactions...")
    df = pd.read_csv(INPUT_FILE)

  
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['drug_a'], row['drug_b'], weight=row['risk_score'])

    print(f"Network Statistics: Nodes={G.number_of_nodes()}, Edges={G.number_of_edges()}")

    
    pagerank = nx.pagerank(G, weight='weight')

  
    degree_centrality = nx.degree_centrality(G)

  
    risk_results = []
    for drug in G.nodes():
        risk_results.append({
            "drug_name": drug,
            "graph_risk_score": pagerank[drug],
            "interaction_count": G.degree(drug),
            "centrality": degree_centrality[drug]
        })

    risk_df = pd.DataFrame(risk_results)
    
   
    if not risk_df.empty:
        max_score = risk_df['graph_risk_score'].max()
        risk_df['normalized_risk_score'] = (risk_df['graph_risk_score'] / max_score) * 100

    risk_df = risk_df.sort_values(by="graph_risk_score", ascending=False)


    output_path = BASE_DIR / "data" / "processed" / "graph_based_drug_risks.csv"
    risk_df.to_csv(output_path, index=False)

    print(f"\nGraph-based risk scoring completed. Saved to: {output_path}")
    print("\nTop 15 Most 'Central' Drugs in Interaction Network:")
    print(risk_df[['drug_name', 'interaction_count', 'normalized_risk_score']].head(15))

if __name__ == "__main__":
    main()
