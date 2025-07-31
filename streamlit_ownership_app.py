
import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import json
import os
import streamlit.components.v1 as components

# Session state initialization
if 'nodes' not in st.session_state:
    st.session_state['nodes'] = set()
if 'edges' not in st.session_state:
    st.session_state['edges'] = set()
if 'default_loaded' not in st.session_state:
    st.session_state['default_loaded'] = False

# Load default data
def load_default_data():
    businesses = pd.read_csv("businesses.csv")
    transactions = pd.read_csv("transactions.csv")
    return businesses, transactions

# Populate session state with default graph
def load_default_graph():
    businesses, transactions = load_default_data()
    for _, txn in transactions.iterrows():
        if txn["role"] == "seller":
            from_biz = txn["business"]
            to_biz = txn["counterparty"]
            classification = txn["classification"]
            st.session_state['nodes'].add((from_biz, classification))
            st.session_state['nodes'].add((to_biz, classification))
            st.session_state['edges'].add((from_biz, to_biz, classification))
    st.session_state['default_loaded'] = True

# Load saved graph from file
def load_saved_graph():
    if os.path.exists("saved_network.json"):
        with open("saved_network.json", "r") as f:
            data = json.load(f)
            st.session_state['nodes'] = set(tuple(x) for x in data.get("nodes", []))
            st.session_state['edges'] = set(tuple(x) for x in data.get("edges", []))
        st.success("Saved layout loaded successfully.")
    else:
        st.error("No saved layout found.")

# Build and display the graph
def build_graph():
    net = Network(height="750px", width="100%", directed=True)
    net.barnes_hut()

    for name, classification in st.session_state['nodes']:
        shape = 'dot' if classification == 'transfer' else 'triangle'
        color = 'skyblue' if shape == 'dot' else 'lightgreen'
        net.add_node(name, label=name, shape=shape, color=color)

    for src, dst, classification in st.session_state['edges']:
        color = 'green' if classification == 'enhance' else 'blue'
        net.add_edge(src, dst, title=classification, color=color)

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

# UI: Controls
st.title("Interactive Economic Network Builder")
st.write("Build or modify your value chain using the interactive graph below.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Load Default Layout"):
        load_default_graph()
with col2:
    if st.button("Load Saved Layout"):
        load_saved_graph()
with col3:
    if st.button("Clear Canvas"):
        st.session_state['nodes'] = set()
        st.session_state['edges'] = set()
        st.session_state['default_loaded'] = False
with col4:
    if st.button("Save Layout"):
        with open("saved_network.json", "w") as f:
            json.dump({
                "nodes": list(st.session_state['nodes']),
                "edges": list(st.session_state['edges'])
            }, f)
        st.success("Layout saved to saved_network.json")

# Add node form
st.subheader("Add New Node")
with st.form("add_node_form"):
    node_name = st.text_input("Node Name")
    classification = st.selectbox("Classification", ["enhance", "transfer"])
    submitted = st.form_submit_button("Add Node")
    if submitted and node_name:
        st.session_state['nodes'].add((node_name, classification))
        st.success(f"Node '{node_name}' added as {classification}")

# Add edge form
st.subheader("Add Edge Between Nodes")
with st.form("add_edge_form"):
    if st.session_state['nodes']:
        node_list = [n[0] for n in st.session_state['nodes']]
        source = st.selectbox("Source Node", node_list, key="src")
        target = st.selectbox("Target Node", node_list, key="tgt")
        edge_type = st.selectbox("Edge Type", ["enhance", "transfer"], key="edge_type")
        edge_submit = st.form_submit_button("Add Edge")
        if edge_submit:
            st.session_state['edges'].add((source, target, edge_type))
            st.success(f"Edge from '{source}' to '{target}' added as {edge_type}")

# Build and show network
build_graph()
