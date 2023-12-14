


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
# import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd

from datetime import datetime

import pickle

import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)


# Read in all meetings and attendance (both full (i.e. dict with party and id) and short (i.e. only name)
meetings_all_commissions_df = pd.read_pickle('../../data/meetings_all_commissions_df_2023-12-12.pkl')
meetings_all_commissions_short_df = pd.read_pickle('../../data/meetings_all_commissions_short_df_2023-12-12.pkl')

# Obtain list of available commissions in dataframe
diff_commissions = list(set(meetings_all_commissions_df["commissie.titel"]))

# Read in commission_overview_df with overall info on each commission
commissions_overview_df = pd.read_pickle('../../data/commissions_overview_df_2023-12-12.pkl')

# Load information about parties
with open(f'../../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)
with open(f'../../data/parlementsleden.pkl', 'rb') as file:
    parlementsleden_all_dict = pickle.load(file)

# Create a list of options for the dropdown
dropdown_options_commission = [{"label": "Alle commissies", "value": "Alle commissies"}] + [{'label': item, 'value': item} for item in diff_commissions]
dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Build app
app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)


# Create the layout
app.layout = html.Div(  
    children=[
        # Header section
        html.Div(
            children=[
                # Title
                html.H1(
                    children="Aanwezigheid Vlaamse parlementsleden",
                    className="header-title",
                    style={"color": "#FFFFFF"}
                ),
                # Description
                html.P(
                    children=(
                        "Het Vlaams Parlement geeft op haar website een overzicht van elke vergadering van elke commissie, en welke vertegenwoordigers hier aanwezig waren. Het Vlaams Parlement stelt deze gegevens ook beschikbaar via een API. Onderstaande visualisaties laten toe om met deze gegevens te interageren."
                        ),
                    className="header-description",
                    style={"color": "#FFFFFF"}
                ),
            ],
            className="section-header",
            style={"background-color": "#222222"} # Set dark background for this section
        ),
        # Persoonlijke informatie
        html.Div(
            children=[
                # Header
                html.Div(
                    children=[
                        html.H2(
                            "Aanwezigheid per parlementslid",
                            className="header-subtitle",
                        ), 
                    ],
                    className="section-header",
                ),
                # Selecting relevant data (party and timeframe)
                html.Div(
                    children=[
                        html.H3(
                            "Selecteer de relevante partij en periode",
                            className="header-subsubtitle",
                        ),
                        # Dropdown to select the political party
                        html.Div(
                            children=[
                                html.Div(
                                    children="Politieke partij?", 
                                    className="menu-title"
                                ),   
                                dcc.Dropdown(
                                    id="dropdown_party",
                                    options=dropdown_options_party,
                                    value="Alle partijen", # default value
                                    clearable=False,
                                    className="dropdown",
                                ),
                            ],
                            className="menu-element"
                        ),
                        # Datepicker to select relevant timeframe
                        html.Div(
                            children=[
                                html.Div(
                                    children="Relevante periode", 
                                    className="menu-title"
                                ),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed=meetings_all_commissions_df["Datum vergadering"].min(),
                                    max_date_allowed=meetings_all_commissions_df["Datum vergadering"].max(),
                                    start_date=meetings_all_commissions_df["Datum vergadering"].min(),
                                    end_date=meetings_all_commissions_df["Datum vergadering"].max(),
                                ),
                            ],
                            className="menu-element"
                        ),
                    ], 
                    className="section-chart",
                ),
                # In hoeveel commissies vast lid? 
                html.Div(
                    children=[
                        # Header
                        html.Div(
                            children=[
                                html.H3(
                                    "In hoeveel commissies is het parlementslid een vast lid?",
                                    className="header-subsubtitle",
                                ),
                            ],
                            className="section-header",
                            ),
                        # Tabel met overzicht aantal commissies vast lid
                        # ...
                    ]
                ),
            ]
        ),
    ]
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


# Define callback to update display based on selected commission and date range
@app.callback(
    [
    Output('pie-chart', 'figure'),
    Output('attendance_per_party_percentage_table', 'children'),
    Output('attendance_per_party_percentage_graph', 'figure')
    # Output('table_attendance_permanent', 'children') # Update the children of 'table_attendance_permanent'
     # Output('table-container', 'children') # Update the children of 'table-container'
     ], 
    [Input('commissie-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_display(commission_value, start_date, end_date):
    # Filter df based on user input
    filtered_df_overview, filtered_df_meetings = filter_data(
    start_date, end_date, commission_value,
    commissions_overview_df, meetings_all_commissions_df)
    
    # # update pie_chart
    # pie_chart = update_pie_charts(filtered_df_overview)
    
    # # update table
    # table = update_table(filtered_df_overview)
    
    # # update table_attendance_permanent
    # table_attendance_permanent = update_attendance_permanent_members(filtered_df_overview, parlementsleden_all_dict)
    
    # # update variable of attendance_per_party
    # attendance_per_party_percentage_df, attendance_per_party_percentage_df_formatted = update_attendance_per_party(filtered_df_overview, fracties_dict_input = fracties_dict)
    
    # # update of table of attendance_per_party
    # attendance_per_party_percentage_table = update_table_indices(attendance_per_party_percentage_df_formatted)
    
    # # update graph of attendance_per_party
    # attendance_per_party_percentage_graph = update_attendance_per_party_graph(attendance_per_party_percentage_df)
    
    
    return [pie_chart, attendance_per_party_percentage_table, attendance_per_party_percentage_graph]
    #, table_attendance_permanent
    # , table
   
    
   
if __name__ == '__main__':
    app.run_server(debug=True)