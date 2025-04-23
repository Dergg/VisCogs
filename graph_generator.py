# It's the Big One!
# Generate a graph from a JSON input, using NetworkX, Dash and Plotly.

import json # Reading the json files from /jsons
import networkx as nx
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import argparse

parser = argparse.ArgumentParser(prog='graph_generator', description='Generate a temporal network graph from JSON files.')
parser.add_argument('infile')
args = parser.parse_args()

try:
    with open(f'./jsons/{args.infile}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f'{args.infile}.json not found in the /jsons folder. Check your spelling and whether the file exists.')

G = nx.DiGraph() # Use a directed graph for directional relationships
# min_year = 3000
# max_year = 0 
MAX_NODES = 50
acq_edges = []
# num_years = [int(item['Year']) for item in data if isinstance(item.get('Year'), str) and item['Year'].isdigit()]

# if num_years:
#     min_year, max_year = min(num_years), max(num_years)
# else:
#     min_year, max_year = 1900, 2025
max_year = 2025
min_year = 1900
span = max_year - min_year if max_year > min_year else 1
mark_step = 10 if span > 50 else 1

#marks = {yr: str(yr) for yr in range(min_year, max_year + 1, mark_step)}
marks = {min_year: str(min_year), max_year: str(max_year)}

for item in data:
    year = item['Year']

    if year.isdigit():
        year = int(year)
    else:
        year = 'Unknown'


    if item['Type'] == 'FND':
        label = item['Label']
        founders = item['Founders']
        G.add_node(label, year=year, founders=founders)

    elif item['Type'] == 'ACQ':
        subject = item['Subject']
        object = item['Object']
        G.add_node(subject, year='Unknown', founders='Unknown')
        G.add_node(object, year='Unknown', founders='Unknown') # Add the nodes if they do not already exist
        acq_edges.append((subject, object, year))


app = dash.Dash(__name__)
layout_cache = {}
def get_pos(graph):
    key = tuple(sorted(graph.nodes()))
    if key not in layout_cache:
        layout_cache[key] = nx.spring_layout(graph, seed=12)
    return layout_cache[key]
app.layout = html.Div([
    html.H1("Temporal Network Entity Relationship Graph"),

    dcc.Slider(
        id='year-slider',
        min=min_year, max=max_year, step=1,
        marks=marks,
        value=min_year,
        tooltip={'always_visible': False, 'placement':'bottom'}
    ),

    dcc.Graph(id='network-graph')
])

@app.callback(
    Output('network-graph', 'figure'),
    Input('year-slider', 'value')
)

def update_graph(selected_year):
    filtered_G = nx.DiGraph()

    for node, data in G.nodes(data=True):
        year = data.get('year', 'Unknown')
        if year == 'Unknown' or (isinstance(year, int) and int(year) <= selected_year):
            filtered_G.add_node(node, year=year, founders=data['founders'])

    if len(filtered_G.nodes) > MAX_NODES:
        limited_nodes = list(filtered_G.nodes)[:MAX_NODES]
        filtered_G = filtered_G.subgraph(limited_nodes).copy()

    for subject, object, year in acq_edges:
        if year !='Unknown' and int(year) <= selected_year:
            if subject in filtered_G.nodes and object in filtered_G.nodes:
                filtered_G.add_edge(subject, object, year=year)

    # pos = nx.spring_layout(filtered_G, seed=12) # Create node positions

    pos = get_pos(filtered_G)

    # Separate new vs. old vs. unknown nodes
    node_x, node_y, node_text = [], [], []
    node_color, node_size, node_symbol = [], [], []

    for node in filtered_G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_data = G.nodes[node]
        node_text.append(f"Label: {node}<br>Founders: {node_data.get('founders', 'Unknown')}")

        year = node_data.get("year", "Unknown")

        if year == "Unknown":
            node_color.append("yellow")  # Unknown year (Gray)
            node_size.append(12)
            node_symbol.append("star")  # Different marker for unknown
        elif int(year) == selected_year:
            node_color.append("red")  # Newly founded in selected year
            node_size.append(15)
            node_symbol.append("circle")
        else:
            node_color.append("blue")  # Existing
            node_size.append(10)
            node_symbol.append("circle")

    # Create Plotly Figure
    fig = go.Figure()

    # Add node trace
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        marker=dict(size=node_size, color=node_color, symbol=node_symbol),
        text=node_text,
        hoverinfo="text"
    ))

    # Edge trace
    edge_x, edge_y = [], []
    for src, targ in filtered_G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[targ]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='gray'),
        hoverinfo='none',
        mode='lines'
    ))

    # Update layout
    fig.update_layout(
        title="Music Label Founding Events",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)