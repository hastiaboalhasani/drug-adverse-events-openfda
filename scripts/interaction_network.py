import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "processed" / "suspect_drug_interactions_reliable.csv"


def build_network(df):

    G = nx.Graph()

    for _, row in df.iterrows():

        drug_a = row["drug_a"]
        drug_b = row["drug_b"]

        weight = row["risk_score"]

        G.add_edge(
            drug_a,
            drug_b,
            weight=weight
        )

    return G


def plot_network(G):

    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(G, k=0.5)

    edges = G.edges(data=True)

    weights = [e[2]["weight"] for e in edges]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=600,
        node_color="skyblue"
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=[w / 2000 for w in weights],
        alpha=0.6
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8
    )

    plt.title("High-Risk Drug Interaction Network")

    plt.axis("off")

    output = BASE_DIR / "data" / "processed" / "drug_interaction_network.png"

    plt.savefig(output, dpi=300)

    print("Network graph saved to:")
    print(output)

    plt.show()


def main():

    print("Loading interaction data...")

    df = pd.read_csv(INPUT_FILE)

    print("Number of interactions:", len(df))

    df = df.sort_values(
        by="risk_score",
        ascending=False
    ).head(50)

    print("Building network graph...")

    G = build_network(df)

    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    plot_network(G)


if __name__ == "__main__":
    main()
