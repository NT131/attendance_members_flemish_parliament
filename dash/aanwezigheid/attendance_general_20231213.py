import dash
from dash import dcc, html
from dash.dependencies import Input, Output
# import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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
                html.Div([
                    dcc.Graph(id='pie-chart'),
                    # Add a dummy component to trigger the update
                    html.Div(id='dummy-trigger', style={'display': 'none'})
                    ]
                ),
                # html.Div(
                    # # Display the table
                    # id='table-container',
                    # className="table",
                    # children=html.P("Tabel niet beschikbaar", style={"color": "red"})
                # )
                html.Div(
                    # Display the table on attendance of members in their permanent commissions
                    id='table_attendance_permanent',
                    className="table",
                    children=html.P("Tabel niet beschikbaar", style={"color": "red"})
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
def update_pie_charts(selected_data):    
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
                textinfo='percent',
                # hovertemplate="aantal leden: %{value}", # see https://plotly.com/python/hover-text-and-formatting/
                hoverinfo='value',
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

    return table  # Return a list containing the table element

def update_attendance_permanent_members(commissions_overview_input_df, parlementsleden_all_dict):
    # Obtain list of all members of parliament
    parlementsleden_list = [parlementsleden_all_dict[member_tuple][0] for member_tuple in parlementsleden_all_dict.keys()]
    # Obtain list of all members of parliament that reside in commissions as permanent member
    all_permanent_members = set()
    for member_list in commissions_overview_input_df['vaste leden']:
        all_permanent_members.update(member_list)
    
    
    # Obtaining actual aggregated counts for how often members were present
    aanwezig_per_lid = attendance_statistics.obtain_aggregated_counts(commissions_overview_input_df['aanwezig_count_vaste'])
    # Set member names as index (to allow easier processing later on)
    aanwezig_per_lid = aanwezig_per_lid.set_index("Member")
    
    
    # There seems to be some members present in `all_permanent_members` (which is based on `commissions_overview_df['vaste leden']`) that are not present in `aanwezig_per_lid` (which is based on `commissions_overview_df['aanwezig_count_vaste']`). We assess which these are, and add them to the `aanwezig_per_lid` dataframe, with count 0.
    # Obtain list of all members of parliament that do not reside in any commission as permanent member
    permanent_members_never_present = [element for element in all_permanent_members if element not in aanwezig_per_lid.index]
    # Add those members to the dataframe, with a count of 0
    for member in permanent_members_never_present:
        aanwezig_per_lid.loc[member] = 0
        
        
    #Create empty dataframe with permanent members, fill with zero (i.e. starting count) and use parmanent members as index
    # Create empty dataframe with permanent members
    member_amount_meetings_pd = pd.DataFrame({'Aantal relevante vergaderingen': 0,
                                              'Aantal bijgewoonde vergaderingen': 0,
                                              'Percentage bijgewoond': 0.0  # Setting the 'Percentage bijgewoond' column as float
                                              }, index=list(all_permanent_members))
    #Iterate over all permanent members of parliament
    for index_members, row_members in member_amount_meetings_pd.iterrows():
        # Iterate for each member through all commissions. 
        # If they are a permanent member, add the amount of meetings of that commission to their key in the dict
        for index_overview, row_overview in commissions_overview_input_df.iterrows():
            if index_members in row_overview["vaste leden"]:
                member_amount_meetings_pd.at[index_members, 'Aantal relevante vergaderingen'] += row_overview['aantal vergaderingen']


    #Iterate over all permanent members of parliament
    for index_members, row_members in member_amount_meetings_pd.iterrows():
        # Extract the aggregated count out of aanwezig_per_lid for the relevant member (i.e. serving as index) 
        # and add to member_amount_meetings_pd at relevant index
        bijgewoonde_verg = aanwezig_per_lid.loc[index_members, "Aggregated_Count"]
        member_amount_meetings_pd.at[index_members, "Aantal bijgewoonde vergaderingen"] = bijgewoonde_verg
        
        # Obtain percentage of attended meetings (taking zero division into account, i.e. with Aantal relevante vergaderingen == 0)
        percentage_attendance = bijgewoonde_verg / row_members['Aantal relevante vergaderingen'] if row_members['Aantal relevante vergaderingen'] != 0 else 0      
        member_amount_meetings_pd.at[index_members, "Percentage bijgewoond"] = percentage_attendance

    # Sort dataframe by percentage attended
    member_amount_meetings_pd = member_amount_meetings_pd.sort_values(by = "Percentage bijgewoond", ascending = False)
    
    
    # Finally, we add the party of the relevant member to the dataframe.
    parties_list = []
    for member in member_amount_meetings_pd.index:
        party = attendance_statistics.find_member(fracties_dict, member)
        parties_list.append(party)   
    member_amount_meetings_pd["Partij"] = parties_list

    
    return member_amount_meetings_pd
     








# Define callback to update display based on selected commission and date range
@app.callback(
    [
    Output('pie-chart', 'figure'),
    Output('table_attendance_permanent', 'children') # Update the children of 'table_attendance_permanent'
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
    
    # update pie_chart
    pie_chart = update_pie_charts(filtered_df_overview)
    
    # update table
    table = update_table(filtered_df_overview)
    
    # update table_attendance_permanent
    table_attendance_permanent = update_attendance_permanent_members(filtered_df_overview, parlementsleden_all_dict)
    
    return [pie_chart, table_attendance_permanent]
    # , table
   
    
   
if __name__ == '__main__':
    app.run_server(debug=True)