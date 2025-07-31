
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load simulation data
@st.cache_data
def load_data():
    businesses = pd.read_csv("businesses.csv")
    transactions = pd.read_csv("transactions.csv")
    return businesses, transactions

businesses, transactions = load_data()

# Build network graph
def visualize_network(businesses, transactions):
    G = nx.DiGraph()
    classification_map = businesses.set_index("name")["type"].to_dict()

    node_shapes = {}
    node_colors = {}

    for _, txn in transactions.iterrows():
        if txn["role"] == "seller":
            from_biz = txn["business"]
            to_biz = txn["counterparty"]
            classification = txn["classification"]

            node_shapes[from_biz] = 'o' if classification == 'transfer' else '^'
            node_shapes[to_biz] = 'o' if transactions[transactions["business"] == to_biz]["classification"].iloc[0] == 'transfer' else '^'

            node_colors[from_biz] = 'skyblue' if node_shapes[from_biz] == 'o' else 'lightgreen'
            node_colors[to_biz] = 'skyblue' if node_shapes[to_biz] == 'o' else 'lightgreen'

            G.add_edge(from_biz, to_biz, classification=classification)

    pos = nx.spring_layout(G, seed=42, k=0.7)

    unique_shapes = set(node_shapes.values())
    for shape in unique_shapes:
        nodes = [n for n in G.nodes() if node_shapes.get(n) == shape]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                               node_shape=shape,
                               node_color=[node_colors[n] for n in nodes],
                               node_size=1500)

    nx.draw_networkx_labels(G, pos, font_size=9)

    for classification in ['enhance', 'transfer']:
        edges = [(u, v) for u, v, d in G.edges(data=True) if d['classification'] == classification]
        nx.draw_networkx_edges(G, pos, edgelist=edges,
                               style='dotted' if classification == 'enhance' else 'solid',
                               edge_color='green' if classification == 'enhance' else 'blue',
                               width=2)

    st.pyplot()

# Display app
st.title("Economic Rewards Simulation - Ownership Graph")
st.write("Use the graph below to explore how ownership and enhancement flow through the network.")
visualize_network(businesses, transactions)
