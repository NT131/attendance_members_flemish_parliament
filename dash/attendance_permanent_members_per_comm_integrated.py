import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc #to use .Col feature for displaying multiple pie charts

import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd

from datetime import datetime

import pickle

import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)



# Read in all meetings and attendance (both full (i.e. dict with party and id) and short (i.e. only name)
relevant_extraction_date = "2023-12-18"

meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df_{relevant_extraction_date}.pkl')
meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df_{relevant_extraction_date}.pkl')

# Obtain list of available commissions in dataframe
diff_commissions = list(set(meetings_all_commissions_df["commissie.titel"]))

# Read in commission_overview_df with overall info on each commission
commissions_overview_df = pd.read_pickle(f'../data/commissions_overview_df_{relevant_extraction_date}.pkl')

# Load information about parties
with open(f'../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)
with open(f'../data/parlementsleden.pkl', 'rb') as file:
    parlementsleden_all_dict = pickle.load(file)

# Create a list of options for the dropdown
dropdown_options_commission = [{"label": "Alle commissies", "value": "Alle commissies"}] + [{'label': item, 'value': item} for item in diff_commissions]
dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Uncomment in integrated approach
# # Build app
# app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)

# Create a container to hold the pie charts
# graphs_container = dbc.Col()
# graphs_container = html.Div(id='graphs_container')



# Create the layout
## Comment in integrated approach
# app.


# layout = html.Div(  
    # children=[
        # # # Header section
        # # html.Div(
            # # children=[
                # # # Title
                # # html.H1(
                    # # children="Aanwezigheid Vlaamse parlementsleden",
                    # # className="header-title",
                    # # style={"color": "#FFFFFF"}
                # # ),
                # # # Description
                # # html.P(
                    # # children=(
                        # # "Het Vlaams Parlement geeft op haar website een overzicht van elke vergadering van elke commissie, en welke vertegenwoordigers hier aanwezig waren. Het Vlaams Parlement stelt deze gegevens ook beschikbaar via een API. Onderstaande visualisaties laten toe om met deze gegevens te interageren."
                        # # ),
                    # # className="header-description",
                    # # style={"color": "#FFFFFF"}
                # # ),
            # # ],
            # # className="section-header",
            # # style={"background-color": "#222222"} # Set dark background for this section
        # # ),
        # # Gemiddelde aanwezigheid vaste leden in commissie + alle leden per partij
        # html.Div(
            # children=[
                # # Header
                # html.Div(
                    # children=[
                        # html.H2(
                            # "Aanwezigheid van parlementsleden per commissie",
                            # className="header-subtitle",
                        # ),
                    # ],
                    # className="section-header",
                # ),
                # # Selecting relevant data
                # html.Div(
                    # children=[
                        # html.H3(
                            # "Selecteer de relevante commissie(s) en de periode.",
                            # className="header-subsubtitle",
                        # ),
                        # # Dropdown to select commission
                        # html.Div(
                            # children=[
                                # html.Div(
                                    # children="Welke commissie?", 
                                    # className="menu-title"
                                # ),
                                # dcc.Dropdown(
                                    # id='commissie-dropdown-per-com',
                                    # options=dropdown_options_commission,
                                    # value="Alle commissies", # default value
                                    # clearable=False,
                                    # className="dropdown",
                                # ),
                            # ],
                            # className="menu-element" 
                        # ),
                        # # Datepicker to select relevant timeframe
                        # html.Div(
                            # children=[
                                # html.Div(
                                    # children="Relevante periode", 
                                    # className="menu-title"
                                # ),
                                # dcc.DatePickerRange(
                                    # id="date-range-per-com",
                                    # min_date_allowed=meetings_all_commissions_df["Datum vergadering"].min(),
                                    # max_date_allowed=meetings_all_commissions_df["Datum vergadering"].max(),
                                    # start_date=meetings_all_commissions_df["Datum vergadering"].min(),
                                    # end_date=meetings_all_commissions_df["Datum vergadering"].max(),
                                # ),
                            # ],
                            # className="menu-element"
                        # ),
                    # ], 
                    # className="section-chart",
                # ),
                # # "Gemiddelde aanwezigheid vaste leden in commissies"
                # html.Div(
                    # children=[
                        # # Header
                        # html.Div(
                            # children=[
                                # html.H3(
                                    # "Gemiddelde aanwezigheid vaste leden in commissies",
                                    # className="header-subsubtitle",
                                # ),
                                # html.P(
                                    # children=(
                                        # "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?"
                                    # ),
                                    # className="header-description",
                                # ),
                            # ],
                            # className="section-header",
                            # ),
                        # # Pie chart
                        # html.Div([
                            # html.Div(id='graphs_container'),
                            # # Add a dummy component to trigger the update
                            # html.Div(id='dummy-trigger', style={'display': 'none'})
                            # ],
                            # className="graph-title",  # Allow word wrapping in titles
                        # ),
                     # ]
                # ),       
            # ],
            # className="wrapper",
        # ),
    # ]
# )

layout = html.Div(  
    children=[
        html.Div(
            children=[
                html.H2(
                    "Aanwezigheid van parlementsleden per commissie",
                    className="header-subtitle",
                ),
            ],
            className="section-header",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(
                            "Selecteer de relevante commissie(s) en de periode.",
                            className="header-subsubtitle",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children="Welke commissie?", 
                                    className="menu-title"
                                ),
                                dcc.Dropdown(
                                    id='commissie-dropdown-per-com',
                                    options=dropdown_options_commission,
                                    value="Alle commissies", # default value
                                    clearable=False,
                                    className="dropdown",
                                ),
                            ],
                            className="menu-element" 
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children="Relevante periode", 
                                    className="menu-title"
                                ),
                                dcc.DatePickerRange(
                                    id="date-range-per-com",
                                    min_date_allowed=meetings_all_commissions_df["Datum vergadering"].min(),
                                    max_date_allowed=meetings_all_commissions_df["Datum vergadering"].max(),
                                    start_date=meetings_all_commissions_df["Datum vergadering"].min(),
                                    end_date=meetings_all_commissions_df["Datum vergadering"].max(),
                                    display_format='DD/MM/YYYY',  # Set the display format to 'dd/mm/yyyy' instead of default 'mm/dd/yyyy'
                                ),
                            ],
                            className="menu-element"
                        ),
                    ], 
                    className="section-chart",
                ),
            ],
            className="wrapper",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(
                            "Gemiddelde aanwezigheid vaste leden in commissies",
                            className="header-subsubtitle",
                        ),
                        html.P(
                            "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?",
                            className="header-description",
                        ),
                    ],
                    className="section-header",
                ),
                html.Div(
                    children=[
                        html.Div(id='graphs_container'),  # Pie chart container
                        html.Div(id='dummy-trigger', style={'display': 'none'})  # Dummy component for update
                    ],
                    className="graph-title",
                ),
            ],
            className="wrapper",
        ),
    ],
    # use CSS flexbox approach to easily structure graphs and titles
    style={"display": "flex", "flex-direction": "column"}
)


#Define function to filter data based on user selection
def filter_data(start_date, end_date, commission_value, 
commissions_overview_df, meetings_all_commissions_df):   
    # Ensure correct date format
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    # Filter i) the DataFrame with all commission meetings based on the commission dropdown value and
    # ii) the overview dataframe based on the commission dropdown value
    if commission_value == "Alle commissies":
        meetings_all_commissions_filtered_df = meetings_all_commissions_df
        commissions_overview_filtered_df = commissions_overview_df
    else:
        meetings_all_commissions_filtered_df = meetings_all_commissions_df[
            meetings_all_commissions_df['commissie.titel'] == commission_value
        ]
        commissions_overview_filtered_df = commissions_overview_df[
            commissions_overview_df['commissie.titel'] == commission_value
        ]

    # Filter DataFrame with all commission meetings further based on the date range
    meetings_all_commissions_filtered_df = meetings_all_commissions_filtered_df[
        (meetings_all_commissions_filtered_df['Datum vergadering'] >= start_date) &
        (meetings_all_commissions_filtered_df['Datum vergadering'] <= end_date)
    ]
    
    
    # Obtain for the filtered df the attendance statistics using imported function
    filtered_df_overview = attendance_statistics.obtain_attendance_statistics(
    commissions_overview_df_input = commissions_overview_filtered_df, 
    meetings_all_commissions_df_input = meetings_all_commissions_filtered_df
    )
    
    # print(filtered_df_overview)
    return (filtered_df_overview, meetings_all_commissions_filtered_df)
    
    
# Update function for pie charts
def update_pie_charts(selected_data):
    graphs = []  # List to store individual pie charts

    # Check if there is data for any commission
    if selected_data is not None and len(selected_data) > 0:
        # Data is available for at least one commission
        for index, row in selected_data.iterrows():
            data_present = row['Gemiddelde aantal aanwezig vaste leden']
            data_absent = row['Gemiddelde aantal afwezig vaste leden']
            data_excused = row['Gemiddelde aantal verontschuldigd vaste leden']

            if not pd.isnull(data_present) and not pd.isnull(data_absent) and not pd.isnull(data_excused):
                labels = ['Aanwezig', 'Afwezig', 'Verontschuldigd']
                sizes = [data_present, data_absent, data_excused]
                colors = ['green', 'red', 'orange']

                # Create a pie chart trace
                pie_chart = go.Pie(
                    labels=labels,
                    values=sizes,
                    textinfo='percent',
                    hovertemplate="<b>aantal leden: %{value}</b>",  # see https://plotly.com/python/hover-text-and-formatting/
                    # hoverinfo='value',
                    hole=0.3,
                    marker=dict(colors=colors),
                    name=row['commissie.titel']
                )
                fig = go.Figure(data=[pie_chart])

                fig.update_layout(
                    title=f"{row['commissie.titel']}",
                    # grid=True,  # Use grid for individual graphs
                    showlegend=True
                )

                graphs.append(dcc.Graph(id=row['commissie.titel'], figure=fig))
            else:
                # If there's insufficient data, create a message instead of a Graph
                message = html.P(
                    f"{row['commissie.titel']}: onvoldoende data beschikbaar.",
                    className="no-data-message"
                )
                graphs.append(message)
                
                # graphs.append(dcc.Graph(
                    # id=row['commissie.titel'],
                    # figure=go.Scatter(
                        # x=[],
                        # y=[],
                        # mode='text',
                        # text=[f"Onvoldoende data beschikbaar voor {row['commissie.titel']}"],
                        # name=row['commissie.titel'],
                        # textposition='top center',
                        # showlegend=False
                    # )
                # ))
    # else:  # No data is available for any commission
        # graphs.append(dcc.Graph(
            # id='no_data_graph',
            # figure=go.Scatter(
                # x=[],
                # y=[],
                # mode='text',
                # text=["Geen data beschikbaar voor alle commissies"],
                # textposition='top center',
                # showlegend=False
            # )
        # ))

    return graphs

#Create function to load app in integrated appraoch
def register_callbacks(app):

    # Define callback to update display based on selected commission and date range
    @app.callback(
        Output('graphs_container', 'children'),
        [Input('commissie-dropdown-per-com', 'value'),
         Input('date-range-per-com', 'start_date'),
         Input('date-range-per-com', 'end_date')]
    )
    def update_display(commission_value, start_date, end_date):
        # Filter df based on user input
        filtered_df_overview, filtered_df_meetings = filter_data(
        start_date, end_date, commission_value,
        commissions_overview_df, meetings_all_commissions_df)
        


    # Update the pie charts based on the selected data
        pie_charts = update_pie_charts(filtered_df_overview)
        
        return pie_charts  # Return the list of graphs as children of graphs_container
       
    
# Comment in integrated approach   
# if __name__ == '__main__':
    # app.run_server(debug=True)