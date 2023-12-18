import dash
from dash import dcc, html
from dash.dependencies import Input, Output
# import plotly.express as px
import plotly.graph_objs as go

import pandas as pd

from datetime import datetime

import pickle

import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)

# # Load data of each meeting for each commission
# with open(f'../../data/vergaderingen_commissies/overall_attendance_dict_2023-12-09.pkl', 'rb') as file:
    # overall_attendance_dict = pickle.load(file)

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

# Create a list of options for the dropdown
dropdown_options_commission = [{"label": "Alle commissies", "value": "Alle commissies"}] + [{'label': item, 'value': item} for item in diff_commissions]
dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Build app
app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)


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
                        # Dropdown to select commission
                        html.Div(
                            children="Welke commissie?", 
                            className="menu-title"),
                        dcc.Dropdown(
                            id='commissie-dropdown',
                            options=dropdown_options_commission,
                            value="Alle commissies", # default value
                            clearable=False,
                            className="dropdown",
                        ),
                        # Dropdown to select the political party
                        html.Div(
                            children=[
                                html.Div(
                                    children="Resultaten voor welke politieke partij?", 
                                    className="menu-title"),   
                                dcc.Dropdown(
                                    id="dropdown_party",
                                    options=dropdown_options_party,
                                    value="Alle partijen", # default value
                                    clearable=False,
                                    className="dropdown",
                                ),
                            ]
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
                            ]
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
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
                # html.Div(
                    # # Display the table
                    # id='table-container',
                    # className="table",
                    # children=html.P("No data available", style={"color": "red"})
                # ),
                html.Div([
                    dcc.Graph(id='pie-chart'),
                    # Add a dummy component to trigger the update
                    html.Div(id='dummy-trigger', style={'display': 'none'})
                    ]
                )
            ],
            className="wrapper",
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
    
    
# Update function for pie charts
def update_pie_chart(selected_data):

    print(selected_data[['Gemiddelde aantal aanwezig alle leden', 'Gemiddelde aantal verontschuldigd alle leden', 'Gemiddelde aantal afwezig alle leden']])
    
    fig = go.Figure()

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
                textinfo='none',
                hoverinfo='label+percent',
                hole=0.3,
                marker=dict(colors=colors),
                name=row['commissie.titel']
            )
            fig.add_trace(pie_chart)
        else:
            fig.add_trace(go.Scatter(
                x=[],
                y=[],
                mode='text',
                text=[f"Onvoldoende data beschikbaar voor {row['commissie.titel']}"],
                name=row['commissie.titel'],
                textposition='top center',
                showlegend=False
            ))

    fig.update_layout(
        title='Gemiddelde aanwezigheid van vaste leden per commissie',
        grid={'rows': 1, 'columns': 1},
        showlegend=True
    )

    return fig

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

    return [table]  # Return a list containing the table element


# Define callback to update display based on selected commission and date range
@app.callback(
    Output('pie-chart', 'figure'),
    # Output('table-container', 'children'),  # Update the children of 'table-container'
    [Input('commissie-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_display(commission_value, start_date, end_date):
    # Filter df based on user input
    filtered_df_overview, filtered_df_meetings = filter_data(
    start_date, end_date, commission_value,
    commissions_overview_df, meetings_all_commissions_df)
    
    # update pie_chart
    pie_chart = update_pie_chart(filtered_df_overview)
    
    # update table
    table = update_table(filtered_df_overview)
    
    return pie_chart
   
    
   
if __name__ == '__main__':
    app.run_server(debug=True)