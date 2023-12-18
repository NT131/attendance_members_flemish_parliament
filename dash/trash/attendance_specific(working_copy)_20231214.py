import dash
from dash import dcc, html
from dash.dependencies import Input, Output
# import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd

from datetime import datetime

from collections import defaultdict

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
                        html.Div(
                            className="table-container",
                            children=[
                                html.Div(
                                    # Display the grouped_by_count_df_table
                                    id='grouped_by_count_df_table',
                                    className="table",
                                    children=html.P("Tabel niet beschikbaar", style={"color": "red"}) # Initial content
                                ),
                            ]
                        )
                        
                    ]
                ),
            ],
            className="wrapper",
        ),
    ]
)


#Define function to filter data based on user selection (not possible to filter commissions_overview_df_input, meetings_all_commissions_df_input on party, so only filter on date)
def filter_data(start_date, end_date, party_value, 
commissions_overview_df_input, meetings_all_commissions_df_input):   
    # Ensure correct date format
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    # Filter DataFrame with all commission meetings further based on the date range
    meetings_all_commissions_filtered_df = meetings_all_commissions_df_input[
        (meetings_all_commissions_df_input['Datum vergadering'] >= start_date) &
        (meetings_all_commissions_df_input['Datum vergadering'] <= end_date)
    ]
    
    
    # Obtain for the filtered df the attendance statistics using imported function
    filtered_df_overview = attendance_statistics.obtain_attendance_statistics(
    commissions_overview_df_input = commissions_overview_df_input, 
    meetings_all_commissions_df_input = meetings_all_commissions_filtered_df
    )
    
    # print(filtered_df_overview)
    return (filtered_df_overview, meetings_all_commissions_filtered_df)


def amount_commissions_as_permanent(commissions_overview_df_input, 
                                    parlementsleden_all_dict_input, 
                                    fracties_dict_input):
    """
    Function to obtain an overview of how many commissions each member of parliament is a permanent member of.
    """
    
     # Count how often a member occurs in the overview of lists of permanent members of commissions
    amount_commissions_members = attendance_statistics.count_member_occurrence(commissions_overview_df_input['vaste leden'])
    
    
    # Group members per amount of commissions
    grouped_by_count = defaultdict(list)
    # Grouping elements by their count
    for name, count in amount_commissions_members:
        grouped_by_count[count].append(name)


    # Add members that are in no commissions at all (with count = 0)
    # Obtain list of all member that are in at least 1 commission as permanent member
    permanent_members = [name for names in grouped_by_count.values() for name in names]
    # Obtain list of all members of parliament (i.e. including those not in any commission)
    parlementsleden_list = [parlementsleden_all_dict[member_tuple][0] for member_tuple in parlementsleden_all_dict_input.keys()]
    # Obtain list of all members of parliament that do not reside in any commission as permanent member
    not_permanent_members = list(set(parlementsleden_list).difference(set(permanent_members)))
    # Add members that are in no commission as permanent member to dict
    grouped_by_count[0] = not_permanent_members
    
    
    # Convert defaultdict to a list of tuples for DataFrame
    grouped_by_count_list = [(name, count) for count, names in grouped_by_count.items() for name in names]
    # Create DataFrame
    grouped_by_count_df = pd.DataFrame(grouped_by_count_list,
                                       columns=['Parlementslid', 'Aantal commissies als vast lid'])
  
  
    # Creating a dictionary mapping members to their parties
    member_to_party = {member[0]: party for party, members in fracties_dict_input.items() for member in members}
    # Filling a list with the corresponding party of each member
    parties_list = [member_to_party.get(member, 'Onbekend') for member in grouped_by_count_df['Parlementslid']]
    # Add list of parties to dataframe as second column (i.e. right after member name)
    grouped_by_count_df.insert(1, "Partij", parties_list)
    
    
    # Drop index
    grouped_by_count_df = grouped_by_count_df.reset_index(drop=True)
    
    
    return grouped_by_count_df

def update_table(df):
   
    # Create table header
    table_header = [html.Tr([html.Th(col) for col in df.columns])]

    # Create table rows using list comprehension
    table_rows = [
        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
        for i in range(len(df))
    ]

    # Assemble the complete table with header and rows
    table = html.Table(table_header + table_rows, className='table')

    return table  # Return a list containing the table element


# Define callback to update display based on selected commission and date range
@app.callback(
    # [
    # Output('pie-chart', 'figure'),
    Output('grouped_by_count_df_table', 'children')
    # ,
    # Output('attendance_per_party_percentage_graph', 'figure')
    # Output('table_attendance_permanent', 'children') # Update the children of 'table_attendance_permanent'
     # Output('table-container', 'children') # Update the children of 'table-container'
     # ]
     , 
    [Input('dropdown_party', 'value'),
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
    
    # update dataframe of amount of permanent commissions per member
    grouped_by_count_df = amount_commissions_as_permanent(
                    commissions_overview_df_input = filtered_df_overview,
                    parlementsleden_all_dict_input = parlementsleden_all_dict, 
                    fracties_dict_input = fracties_dict)
    
    # update table of amount of permanent commissions per member
    grouped_by_count_df_table = update_table(grouped_by_count_df)
    
    return grouped_by_count_df_table
   
    
   
if __name__ == '__main__':
    app.run_server(debug=True)