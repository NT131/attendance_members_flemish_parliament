import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Load the data
df = pd.read_pickle("attendance_permanent_members.pkl")

# external_stylesheets = [
    # {
        # "href": (
            # "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap"
        # ),
        # "rel": "stylesheet",
    # },
# ]

# Create the app
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, external_stylesheets=[
# 'https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap', 
# # assets_folder='./assets'
# # '/assets/style.css' # Relative path to your CSS file
# ])
app = dash.Dash(__name__, assets_folder='../assets') # Relative path to the folder of css file



app.title = "Aanwezigheid in commissies waarvan parlementsleden vast lid zijn" # title of tab in browser


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

    df_filtered = df_filtered.sort_values(by="Percentage bijgewoond", ascending=False)  # Sort by aggregate count

    table_data = html.Table(
        # Header
        [html.Tr([
            html.Th("Parlementslid"), 
            html.Th("Partij"), 
            html.Th("Aantal relevante vergaderingen"), 
            html.Th("Aantal bijgewoonde vergaderingen"), 
            html.Th("Percentage bijgewoond")
        ])] +
        # Body
        [html.Tr([
            html.Td(df_filtered.index[i]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Partij"]),
            html.Td(df_filtered.loc[df_filtered.index[i], "Aantal relevante vergaderingen"],
                style={"text-align": "right"}), # Ensure right sided alignent for this column
            html.Td(df_filtered.loc[df_filtered.index[i], "Aantal bijgewoonde vergaderingen"],
                style={"text-align": "right"}), # Ensure right sided alignent for this column
            html.Td(f'{df_filtered.loc[df_filtered.index[i], "Percentage bijgewoond"]:.1%}', # show in percentages
                style={"text-align": "right"}), # Ensure right sided alignent for this column
        ])for i in range(len(df_filtered))]  
    )

    return table_data

# Create the layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                # Title
                html.H1(
                    children="Aanwezigheid in commissies waarin parlementslid vast lid is",
                    className="header-title"
                ),
                html.P(
                    children=(
                        "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?"
                        ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                        children="Resultaten voor welke politieke partij?", 
                        className="menu-title"),
                        # Dropdown to select the political party
                        dcc.Dropdown(
                            id="party",
                            options=[
                                {"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in df["Partij"].unique() if party
                                ],  # Exclude null parties
                            value="Alle partijen", # default value
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    # Graph of the average attendance per member
                    children=dcc.Graph(
                        id="average-attendance",
                        # config={"displayModeBar": False}, # Remove the floating toolbar that Plotly shows by default
                    ),
                    className="card",
                ),
                html.Div(
                # Table of the attendance data for each member
                    children=[
                        html.H2(
                            "Aanwezigheidsgegevens",
                            className="header-title",
                            style={"color": "#333333", "padding": "10px"} # ensure header has dark font since no dark background as in main title
                        ),
                        html.P(
                            children=(
                                "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?"
                                ),
                            className="header-description",
                            style={"color": "#333333"} # ensure header has dark font since no dark background as in main title
                        ),
                    ]
                ),
                html.Div(
                    # Display the table
                    children=html.Div(
                        id="attendance-data",
                        className="table"
                        ),
                ),
            ],
            className="wrapper",
        ),
    ]
)


# Update average attendance graph based on party selection
@app.callback(Output("average-attendance", "figure"), Input("party", "value")
)
def update_graph(selected_party):
    if selected_party == "Alle partijen":
        df_filtered = df.copy()
    else:
        df_filtered = df[df["Partij"] == selected_party]

    df_filtered = df_filtered.sort_values(by="Percentage bijgewoond", ascending=False)  # Sort by aggregate count

    data = [{
        "x": df_filtered.index,
        "y": df_filtered["Percentage bijgewoond"],
        "type": "bar",
        "marker": {"color": [party_colors.get(party, "grey") for party in df_filtered['Partij']]},  # Set color based on party
        "hovertemplate": "<b>%{x}</b><br>"
                         "Partij: %{text[0]}<br>"
                         "Aantal relevante vergaderingen: %{text[1]}<br>"
                         "Aantal bijgewoonde vergaderingen: %{text[2]}<br>"
                         "Percentage bijgewoond: %{text[3]:.1%}<extra></extra>",
        "text": df_filtered[['Partij', 'Aantal relevante vergaderingen', 'Aantal bijgewoonde vergaderingen', 'Percentage bijgewoond']].values.tolist(),
    }]

    return {
        "data": data,
        "layout": {
            "title": "Aanwezigheid van parlementsleden in commissies waarvan ze vast lid zijn",
            "xaxis": {"title": "Parlementslid", "tickangle": -45, "tickfont": {"size": 10}, "automargin": True},
            "yaxis": {"title": "Aantal bijgewoonde vergaderingen"},
        },
    }

# Update table data based on party selection
@app.callback(Output("attendance-data", "children"), Input("party", "value"))
def update_table(selected_party):
    return get_table_data(selected_party)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
