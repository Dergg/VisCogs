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
    year = item.get('Year', 'Unknown')

    if isinstance(year, str) and year.isdigit():
        year = int(year)
    elif not isinstance(year, int):
        year = 'Unknown'


    if item.get('Type') == 'FND':
        label = item['Label']
        founders = item.get('Founders', 'Unknown')
        G.add_node(label, year=year, founders=founders)

    elif item.get('Type') == 'ACQ':
        subject = item.get('Subject', 'Unknown')
        object = item.get('Object', 'Unknown')
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
        value=max_year,
        tooltip={'always_visible': False, 'placement':'bottom'}
    ),

    dcc.Input(id='label-filter', type='text', placeholder='Enter label name'),

    dcc.Graph(id='network-graph')
])

@app.callback(
    Output('network-graph', 'figure'),
    Input('year-slider', 'value'),
    Input('label-filter', 'value')
)

def update_graph(selected_year, label_filter):
    print("Callback triggered.")
    filtered_G = nx.DiGraph()
    # Step 1: Define base_graph (which nodes to show)
    if label_filter:
        search_term = label_filter.strip().lower()
        matched_nodes = [n for n in G.nodes if search_term in n.lower()]
        print(f'Matched nodes (first {min(10, len(matched_nodes))}): {matched_nodes[:(min(9, len(matched_nodes) - 1))]}')
        rel = set()
        for node in matched_nodes:
            rel.add(node)
            rel.add(nx.ancestors(G, node))
            rel.add(nx.desceneants(G, node))
        print(f'Total related nodes: {len(rel)}')
    else:
        rel = set(G.nodes)

    filtered_G = nx.DiGraph()

    # Step 2: Filter by year
    print("Filtering by year")
    filtered_G = nx.DiGraph()
    for node in rel:
        data = G.nodes[node]
        year = data.get("year", "Unknown")
        if year == "Unknown" or (isinstance(year, int) and year <= selected_year):
            filtered_G.add_node(node, year=year, founders=data.get('Founders', 'Unknown'))

    for subject, object, year in acq_edges:
        # Ensure valid year and presence in filtered nodes
        if (
            subject in filtered_G.nodes and
            object in filtered_G.nodes and
            (year == 'Unknown' or (isinstance(year, int) and year <= selected_year))
        ):
            filtered_G.add_edge(subject, object, year=year, event_type='ACQ')

    print(f'Final graph has {len(filtered_G.nodes)} nodes and {len(filtered_G.edges)} edges.')

    # If no nodes after filtering, return empty figure
    if not filtered_G.nodes:
        return go.Figure(layout=go.Layout(title='No data to display. :('))

    # Step 3: Positioning and node visuals
    pos = nx.spring_layout(filtered_G, seed=12)

    node_x, node_y, node_text = [], [], []
    node_color, node_size, node_symbol = [], [], []

    for node in filtered_G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_data = filtered_G.nodes[node]
        node_text.append(f"Label: {node}<br>Founders: {node_data.get('founders', 'Unknown')}")
        year = node_data.get("year", "Unknown")

        if year == "Unknown":
            node_color.append("yellow")
            node_size.append(12)
            node_symbol.append("star")
        elif int(year) == selected_year:
            node_color.append("red")
            node_size.append(15)
            node_symbol.append("circle")
        else:
            node_color.append("blue")
            node_size.append(10)
            node_symbol.append("circle")

    # Step 4: Draw edges
    edge_x, edge_y, edge_texts = [], [], []
    for u, v, edge_data in filtered_G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        year = edge_data.get('year', 'Unknown')
        edge_texts.append(f"{edge_data.get('type', 'ACQ')} ({year}) from {u} → {v}")

    # Step 5: Build the figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='gray'),
        hoverinfo='text',
        text=edge_texts,
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(size=node_size, color=node_color, symbol=node_symbol),
        text=node_text,
        hoverinfo='text'
    ))

    fig.update_layout(
        title="VisCogs: a new history of the recording industry",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)