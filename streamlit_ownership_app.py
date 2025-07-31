
import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components

# Load data
@st.cache_data
def load_data():
    businesses = pd.read_csv("businesses.csv")
    transactions = pd.read_csv("transactions.csv")
    return businesses, transactions

businesses, transactions = load_data()

# Build interactive network with PyVis
def visualize_network_pyvis(businesses, transactions):
    G = nx.DiGraph()

    node_types = businesses.set_index("name")["type"].to_dict()
    node_shapes = {}
    node_colors = {}

    for _, txn in transactions.iterrows():
        if txn["role"] == "seller":
            from_biz = txn["business"]
            to_biz = txn["counterparty"]
            classification = txn["classification"]

            node_shapes[from_biz] = 'dot' if classification == 'transfer' else 'triangle'
            node_shapes[to_biz] = 'dot' if transactions[transactions["business"] == to_biz]["classification"].iloc[0] == 'transfer' else 'triangle'

            node_colors[from_biz] = 'skyblue' if node_shapes[from_biz] == 'dot' else 'lightgreen'
            node_colors[to_biz] = 'skyblue' if node_shapes[to_biz] == 'dot' else 'lightgreen'

            G.add_edge(from_biz, to_biz, title=f"{classification}", classification=classification)

    net = Network(height="750px", width="100%", directed=True)
    net.barnes_hut()

    for node in G.nodes():
        net.add_node(node,
                     label=node,
                     shape=node_shapes.get(node, 'dot'),
                     color=node_colors.get(node, 'gray'))

    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, title=d['classification'], color='green' if d['classification'] == 'enhance' else 'blue')

    net.set_options('''
    var options = {
      "interaction": {
        "hover": true,
        "dragNodes": true,
        "navigationButtons": true
      },
      "manipulation": {
        "enabled": true
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 250
        },
        "minVelocity": 0.75
      }
    }
    ''')

    net.save_graph("graph.html")
    HtmlFile = open("graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=800, scrolling=True)

# Display app
st.title("Interactive Economic Rewards Network")
st.write("Explore, drag, and reposition businesses in the network graph below.")

visualize_network_pyvis(businesses, transactions)
