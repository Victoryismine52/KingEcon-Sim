
import streamlit as st
import json
from pyvis.network import Network
import streamlit.components.v1 as components

# Initialize session state
if 'node_types' not in st.session_state:
    st.session_state['node_types'] = {}  # key: type_name, value: dict with shape, color
if 'nodes' not in st.session_state:
    st.session_state['nodes'] = []  # list of (node_id, type_name)
if 'edges' not in st.session_state:
    st.session_state['edges'] = []  # list of (from_node, to_node)

st.title("🌾 Value Chain Designer")

# --- SECTION 1: Node Type Manager ---
st.subheader("1️⃣ Define Node Types")

with st.form("add_node_type_form"):
    type_name = st.text_input("Node Type Name")
    shape = st.selectbox("Shape", ["dot", "triangle", "box", "ellipse", "star"])
    color = st.color_picker("Color", "#00ccff")
    submit_type = st.form_submit_button("Add / Update Node Type")

if submit_type and type_name:
    st.session_state['node_types'][type_name] = {"shape": shape, "color": color}
    st.success(f"Node type '{type_name}' saved.")

# Display current node types
if st.session_state['node_types']:
    st.write("### Defined Node Types:")
    for tname, tinfo in st.session_state['node_types'].items():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        col1.write(f"**{tname}**")
        col2.write(f"Shape: {tinfo['shape']}")
        col3.write(f"Color: {tinfo['color']}")
        if col4.button("❌", key=f"delete_{tname}"):
            del st.session_state['node_types'][tname]
            st.experimental_rerun()

# --- SECTION 2: Node Placement ---
st.subheader("2️⃣ Add Nodes to the Graph")

if st.session_state['node_types']:
    with st.form("add_node_instance"):
        instance_id = st.text_input("Node ID")
        selected_type = st.selectbox("Node Type", list(st.session_state['node_types'].keys()))
        node_submit = st.form_submit_button("Add Node")

    if node_submit and instance_id:
        st.session_state['nodes'].append((instance_id, selected_type))
        st.success(f"Node '{instance_id}' added as type '{selected_type}'.")

# --- SECTION 3: Edge Creator ---
st.subheader("3️⃣ Define Workflow (Edges)")
if st.session_state['nodes']:
    node_ids = [n[0] for n in st.session_state['nodes']]
    with st.form("add_edge_form"):
        from_node = st.selectbox("From Node", node_ids, key="from_node")
        to_node = st.selectbox("To Node", node_ids, key="to_node")
        edge_submit = st.form_submit_button("Add Edge")
    if edge_submit:
        st.session_state['edges'].append((from_node, to_node))
        st.success(f"Edge from '{from_node}' to '{to_node}' added.")

# --- SECTION 4: Visualize Network ---
st.subheader("4️⃣ Value Chain Preview")

def draw_network():
    net = Network(height="600px", width="100%", directed=True)
    net.barnes_hut()
    for node_id, type_name in st.session_state['nodes']:
        t = st.session_state['node_types'][type_name]
        net.add_node(node_id, label=node_id, shape=t['shape'], color=t['color'])
    for src, tgt in st.session_state['edges']:
        net.add_edge(src, tgt)
    net.set_options('''
        var options = {
          "interaction": {
            "hover": true,
            "dragNodes": true,
            "navigationButtons": true
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
    net.save_graph("value_chain_graph.html")
    HtmlFile = open("value_chain_graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=600, scrolling=True)

draw_network()

# --- SECTION 5: Save and Clear ---
st.subheader("5️⃣ Export / Reset")

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Save Value Chain"):
        config = {
            "node_types": st.session_state['node_types'],
            "nodes": st.session_state['nodes'],
            "edges": st.session_state['edges']
        }
        with open("value_chain_config.json", "w") as f:
            json.dump(config, f, indent=2)
        st.success("Value chain saved to value_chain_config.json")

with col2:
    if st.button("♻️ Clear All"):
        st.session_state['node_types'] = {}
        st.session_state['nodes'] = []
        st.session_state['edges'] = []
        st.experimental_rerun()
