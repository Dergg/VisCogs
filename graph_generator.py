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

G = nx.Graph()

for item in data:
    label = item['Label']
    year = item['Year']
    founders = item['Founders']

    if year.isdigit():
        year = int(year)
    else:
        year = 'Unknown'

    G.add_node(label, year=year, founders=founders)

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Temporal Network Entity Relationship Graph"),

    dcc.Slider(
        id='year-slider',
        min=1980, max=2025, step=1,
        marks={year:str(year) for year in range(1980, 2025, 5)},
        value=2025,
    ),

    dcc.Graph(id='network-graph')
])

@app.callback(
    Output('network-graph', 'figure'),
    Input('year-slider', 'value')
)

def update_graph(selected_year):
    filtered_G = nx.Graph()

    for node, data in G.nodes(data=True):
        year = data.get('year', 'Unknown')
        if year == 'Unknown' or (isinstance(year, int) and int(year) <= selected_year):
            filtered_G.add_node(node, year=year, founders=data['founders'])

    pos = nx.spring_layout(filtered_G, seed=12) # Create node positions

    # Separate new vs. old vs. unknown nodes
    node_x, node_y, node_text = [], [], []
    node_color, node_size, node_symbol = [], [], []

    for node in filtered_G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_data = G.nodes[node]
        node_text.append(f"Label: {node}<br>Founders: {node_data['founders']}")

        year = node_data["year"]

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