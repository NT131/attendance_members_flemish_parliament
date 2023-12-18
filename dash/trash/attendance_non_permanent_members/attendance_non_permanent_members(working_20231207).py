import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Load the data
df = pd.read_pickle("attendance_non_permanent_members.pkl")

# Create the app
app = dash.Dash(__name__)

# Dictionary mapping parties to colors
# party_colors = {
    # "cd&v": "orange",
    # "Vooruit": "red",
    # "Groen": "green",
    # "N-VA": "yellow",
    # "Open-VLD": "blue",
    # "Onafhankelijk": "grey",
    # "PVDA": "darkred",
    # "Vlaams Belang": "black",
# }
# # Use colours obtained from website: manual insertion or reading in dict
party_colors = {'Groen': '83de62',
    'Onafhankelijke': '787878',
    'Vooruit': 'FF2900',
    'Vlaams Belang': 'ffe500',
    'cd&v': 'f5822a',
    'N-VA': 'ffac12',
    'Open Vld': '003d6d',
    'PVDA': 'AA050E'
 }
 
 # party_colors = pd.read_pickle("partij_kleur_dict.pkl")


# Create a function to generate the table data
def get_table_data(selected_party):
    if selected_party == "Alle partijen":
        df_filtered = df.copy()
    else:
        df_filtered = df[df["Partij"] == selected_party].copy()

    df_filtered = df_filtered.sort_values(by="Aggregated_Count", ascending=False)  # Sort by aggregate count

    table_data = html.Table(
        # Header
        [html.Tr([html.Th("Lid"), html.Th("Partij"), html.Th("Totaal aantal vergaderingen"), html.Th("Extra commissies"), html.Th("Vaste commissies")])] +
        # Body
        [html.Tr([
            html.Td(df_filtered.index[i]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Partij"]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Aggregated_Count"]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Aantal commissies extra aanwezig"]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Aantal commissies waarin vast lid"])
        ]) for i in range(len(df_filtered))]
    )

    return table_data

# Create the layout
app.layout = html.Div([
    # Title
    html.H1("Aanwezigheid in commissies waarin parlementslid geen vast lid is"),
    
    # Dropdown to select the political party
    dcc.Dropdown(
        id="party",
        options=[{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in df["Partij"].unique() if party],  # Exclude null parties
        value="Alle partijen",
    ),

    # Graph of the average attendance per member
    dcc.Graph(
        id="average-attendance",
    ),

    # Table of the attendance data for each member
    html.H2("Aanwezigheidsgegevens"),

    # Display the table
    html.Div(id="attendance-data"),
])

# Update average attendance graph based on party selection
@app.callback(Output("average-attendance", "figure"), Input("party", "value"))
def update_graph(selected_party):
    if selected_party == "Alle partijen":
        df_filtered = df.copy()
    else:
        df_filtered = df[df["Partij"] == selected_party]

    df_filtered = df_filtered.sort_values(by="Aggregated_Count", ascending=False)  # Sort by aggregate count

    data = [{
        "x": df_filtered.index,
        "y": df_filtered["Aggregated_Count"],
        "type": "bar",
        "marker": {"color": [party_colors.get(party, "grey") for party in df_filtered['Partij']]},  # Set color based on party
        "hovertemplate": "<b>%{x}</b><br>"
                         "Partij: %{text[0]}<br>"
                         "Totaal aantal vergaderingen: %{text[1]}<br>"
                         "Extra commissies: %{text[2]}<br>"
                         "Vaste commissies: %{text[3]}<extra></extra>",
        "text": df_filtered[['Partij', 'Aggregated_Count', 'Aantal commissies extra aanwezig', 'Aantal commissies waarin vast lid']].values.tolist(),
    }]

    return {
        "data": data,
        "layout": {
            "title": "Aanwezigheid van parlementsleden in commissies waarin geen vast lidmaatschap",
            "xaxis": {"title": "Lid", "tickangle": -45, "tickfont": {"size": 10}, "automargin": True},
            "yaxis": {"title": "Aantal vergaderingen"},
        },
    }

# Update table data based on party selection
@app.callback(Output("attendance-data", "children"), Input("party", "value"))
def update_table(selected_party):
    return get_table_data(selected_party)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
