import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
from plotly.subplots import make_subplots



import numpy as np
import pandas as pd

from datetime import datetime
import locale

import pickle

import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)


# Set the locale to Dutch (Belgian)
locale.setlocale(locale.LC_TIME, 'nl_BE.utf8')  # Set appropriate locale for Dutch

# Read in all meetings and attendance (both full (i.e. dict with party and id) and short (i.e. only name)
# relevant_extraction_date = "2023-12-18"

#meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df_{relevant_extraction_date}.pkl')
#meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df_{relevant_extraction_date}.pkl')
meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df.pkl')
meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df.pkl')


# Obtain date of most recent meeting in dataset + format to e.g. "15 februari 2023"
date_most_recent_meeting_per_party = meetings_all_commissions_df['Datum vergadering'].max().strftime('%d %B %Y')

# Obtain list of available commissions in dataframe
diff_commissions = list(set(meetings_all_commissions_df["commissie.titel"]))

# Read in commission_overview_df with overall info on each commission
# commissions_overview_df = pd.read_pickle(f'../data/commissions_overview_df_{relevant_extraction_date}.pkl')
commissions_overview_df = pd.read_pickle(f'../data/commissions_overview_df.pkl')


# Load information about parties
with open(f'../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)
with open(f'../data/parlementsleden.pkl', 'rb') as file:
    parlementsleden_all_dict = pickle.load(file)

# Create a list of options for the dropdown
dropdown_options_commission = [{"label": "Alle commissies", "value": "Alle commissies"}] + [{'label': item, 'value': item} for item in diff_commissions]
dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Create a default value for amount_meetings, i.e. relevant meetings
amount_meetings_per_party = len(meetings_all_commissions_df)  # Set amount of all meetings as default, it will be updated in the callback


# Build app
app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)

## Comment in integrated approach
# app.
# Create the layout
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
        # # Aanwezigheid leden per partij
        # html.Div(
            # children=[
                # # Header
                # html.Div(
                    # children=[
                        # html.H2(
                            # "Aanwezigheidsgegevens van parlementsleden per partij",
                            # className="header-subsubtitle",
                        # ),
                        # html.P(
                            # children=(
                                # "Welke partij woonde het meest frequent vergaderingen van commissies bij?"
                            # ),
                            # className="header-description",
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
                                    # id='commissie-dropdown-per-party',
                                    # options=dropdown_options_commission,
                                    # value="Alle commissies", # default value
                                    # clearable=False,
                                    # className="dropdown",
                                # ),
                            # ],
                            # className="menu-element" 
                        # ),
                        # # # Dropdown to select the political party
                        # # html.Div(
                            # # children=[
                                # # html.Div(
                                    # # children="Resultaten voor welke politieke partij?", 
                                    # # className="menu-title"),   
                                # # dcc.Dropdown(
                                    # # id="dropdown_party",
                                    # # options=dropdown_options_party,
                                    # # value="Alle partijen", # default value
                                    # # clearable=False,
                                    # # className="dropdown",
                                # # ),
                            # # ]
                        # # ),
                        # # Datepicker to select relevant timeframe
                        # html.Div(
                            # children=[
                                # html.Div(
                                    # children="Relevante periode", 
                                    # className="menu-title"
                                # ),
                                # dcc.DatePickerRange(
                                    # id="date-range-per-party",
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
                # # Attendance of commissions per party
                # html.Div(
                    # children=[    
                        # # Graph attendance_per_party
                        # html.Div([
                            # dcc.Graph(id='attendance_per_party_percentage_graph')
                            # ]
                        # ),
                        # # Table attendance_per_party
                        # html.Div(
                            # className="table-container",
                            # children=[
                                # html.Div(
                                    # # Display the attendance_per_party_percentage_table
                                    # id='attendance_per_party_percentage_table',
                                    # className="table",
                                    # children=html.P("Tabel niet beschikbaar", style={"color": "red"})
                                # ),
                            # ]
                        # )
                    # ],
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
                    "Aanwezigheidsgegevens van parlementsleden per partij",
                    className="header-subsubtitle",
                ),
                html.P(
                    "Welke partij woonde het meest frequent vergaderingen van commissies bij?",
                    className="header-description",
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
                                    id='commissie-dropdown-per-party',
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
								html.Div(
									# Display the most recent meeting date
									id='most-recent-date-per-party',
									children=f"Laatste update: {date_most_recent_meeting_per_party}",
									style={'font-style': 'italic'}
								),
                                dcc.DatePickerRange(
                                    id="date-range-per-party",
                                    min_date_allowed=meetings_all_commissions_df["Datum vergadering"].min(),
                                    max_date_allowed=meetings_all_commissions_df["Datum vergadering"].max(),
                                    start_date=meetings_all_commissions_df["Datum vergadering"].min(),
                                    end_date=meetings_all_commissions_df["Datum vergadering"].max(),
                                    display_format='DD/MM/YYYY',  # Set the display format to 'dd/mm/yyyy' instead of default 'mm/dd/yyyy'
                                ),
                            ],
                            className="menu-element"
                        ),
						# Display impact of data selection (i.e. how many meetings are taken into account)	
						html.Div(
							children=[
								html.Div(id='amount_meetings_per_party',
										 children=f"Deze selectie resulteert in {amount_meetings_per_party} relevante vergaderingen."),
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
                # Graph attendance_per_party
                dcc.Graph(id='attendance_per_party_percentage_graph'),
                # Table attendance_per_party
                html.Div(
                    className="table-container",
                    children=[
                        html.Div(
                            # Display the attendance_per_party_percentage_table
                            id='attendance_per_party_percentage_table',
                            className="table",
                            children=html.P("Tabel niet beschikbaar", style={"color": "red"})
                        ),
                    ]
                )
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
    
	
def update_attendance_per_party(commissions_overview_df_input, fracties_dict_input):
    """
    To obtain an overview of how members of each party attend meetings, we group the counts of each members along the party the are member to. We use the helper function get_overall_presence() to obtain this for each attendance status ('Aanwezig', 'Afwezig', 'Verontschuldigd').
    
    Then we actually obtain the attendance status. We do this, accross all members, so not limited to the permanent members. This might provide a better picture, since this indicates whether members of parliament took care in ensuring their commission was attended properly, even if not by them personally.

    The resulting dictionaries do not necessarily have the same keys. If a certain party was never absent, no key for that party will be available in the dictionary of the absent counts. Hence, we add keys (with a zero count) if necessary.

    """

    # Obtain attendance for each attendance status, and for each party
    party_count_aanwezig = attendance_statistics.get_overall_presence(commissions_overview_df_input["aanwezig_count_alle"], fracties_dict)
    party_count_afwezig = attendance_statistics.get_overall_presence(commissions_overview_df_input["afwezig_count_alle"], fracties_dict)
    party_count_verontschuldigd = attendance_statistics.get_overall_presence(commissions_overview_df_input["verontschuldigd_count_alle"], fracties_dict)
    
    
    # Modify dictionaries to ensure all have the same parties (i.e. if certain party never afwezig: create new entry with 0)
    for attendance_dict in [party_count_aanwezig, party_count_afwezig, party_count_verontschuldigd]:
        for party in fracties_dict.keys():
            if party not in attendance_dict.keys():
                attendance_dict[party] = 0

    
    # Then we create a dataframe of these dictionaries, to ease up further assessment. We also include a total count per party. Furthermore, we create a dictionary with the counts as percentages, which is easier for the graphical respresentation later on. 

    # Group attendance-statuses per party in dataframe
    attendance_per_party = pd.DataFrame(data = [party_count_aanwezig, party_count_afwezig, party_count_verontschuldigd],
                                        index = ["Aanwezig", "Afwezig", "Verontschuldigd"])
    # Add sum for each party (i.e. column)
    attendance_per_party.loc['Totaal'] = attendance_per_party.sum()


    # Calculate percentages using numpy
    percentages = (attendance_per_party.values / attendance_per_party.values[-1, :]) * 100
    # Create a new DataFrame with the calculated percentages
    attendance_per_party_percentages = pd.DataFrame(percentages, 
                                                    columns = attendance_per_party.columns,
                                                    index = attendance_per_party.index)
    
    
    # Format the DataFrame to display up to 2 decimals after the comma
    attendance_per_party_percentage_formatted = attendance_per_party_percentages.map(lambda x: f'{x:.2f}')
    
    # return both formatted and unformatted df (formatted interesting for html table, since formatting must be done beforehand)
    return (attendance_per_party_percentages, attendance_per_party_percentage_formatted)
    

# Function to update the attendance per party graph
def update_attendance_per_party_graph(attendance_per_party_percentage):
    # Sort parties based on 'aanwezig' values
    sorted_parties = attendance_per_party_percentage.loc['Aanwezig'].sort_values(ascending=True).index
    sorted_aanwezig = attendance_per_party_percentage.loc['Aanwezig', sorted_parties]
    sorted_afwezig = attendance_per_party_percentage.loc['Afwezig', sorted_parties]
    sorted_verontschuldigd = attendance_per_party_percentage.loc['Verontschuldigd', sorted_parties]

    # Calculate the cumulative heights for each section
    bars_aanwezig = sorted_aanwezig.values
    bars_afwezig = sorted_afwezig.values
    bars_verontschuldigd = sorted_verontschuldigd.values

    cum_bars_afwezig = np.add(bars_aanwezig, bars_afwezig)
    cum_bars_verontschuldigd = np.add(cum_bars_afwezig, bars_verontschuldigd)

    bar_height = 0.5  # Height of each bar section
    index = np.arange(len(sorted_parties))

    # Create traces for each bar section
    trace_aanwezig = go.Bar(y=sorted_parties, x=bars_aanwezig, orientation='h', name='Aanwezig', marker=dict(color='green'), hoverinfo='x', hovertemplate='%{x:.1f}%')  # Display value on hover, in percentage format
    trace_afwezig = go.Bar(y=sorted_parties, x=bars_afwezig, orientation='h', name='Afwezig', marker=dict(color='red'), hoverinfo='x', hovertemplate='%{x:.1f}%')  # Display value on hover, in percentage format
    trace_verontschuldigd = go.Bar(y=sorted_parties, x=bars_verontschuldigd, orientation='h', name='Verontschuldigd', marker=dict(color='orange'), hoverinfo='x', hovertemplate='%{x:.1f}%')  # Display value on hover, in percentage format

    data = [trace_aanwezig, trace_afwezig, trace_verontschuldigd]

    # Layout
    layout = go.Layout(
        barmode='stack',
        title='Aanwezigheid verschillende partijen in commissies',
        xaxis=dict(title='Aanwezigheid (%)', range=[0, 100]), # set range to max 100, to avoid extra space at right side of label '100').
        yaxis=dict(title='Partijen'),
        legend=dict(x=0.1, y=1.15),
        margin=dict(l=150)  # Adjust margin to accommodate labels
    )

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

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

# modified version of update_table() to also show indices as column
def update_table_indices(df):
    # Create table header including indices
    table_header = [
        html.Tr([html.Th('Index')] + [html.Th(col) for col in df.columns])
    ]

    # Create table rows including indices
    table_rows = [
        html.Tr([html.Td(df.index[i])] + [html.Td(df.iloc[i][col]) for col in df.columns])
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
     







#Create function to load app in integrated appraoch
def register_callbacks(app):
    # Define callback to update display based on selected commission and date range
    @app.callback(
        [
        Output('amount_meetings_per_party', 'children'),
	   	Output('attendance_per_party_percentage_table', 'children'),
        Output('attendance_per_party_percentage_graph', 'figure'),
         ], 
        [Input('commissie-dropdown-per-party', 'value'),
         Input('date-range-per-party', 'start_date'),
         Input('date-range-per-party', 'end_date')]
    )
    def update_display(commission_value, start_date, end_date):
        # Filter df based on user input
        filtered_df_overview, filtered_df_meetings = filter_data(
        start_date, end_date, commission_value,
        commissions_overview_df, meetings_all_commissions_df)
		
		# Obtain count of relevant data, after filtering
        amount_meetings_per_party = len(filtered_df_meetings)
        
        
        # # update table
        # table = update_table(filtered_df_overview)
        
        # update table_attendance_permanent
        table_attendance_permanent = update_attendance_permanent_members(filtered_df_overview, parlementsleden_all_dict)
        
        # update variable of attendance_per_party
        attendance_per_party_percentage_df, attendance_per_party_percentage_df_formatted = update_attendance_per_party(filtered_df_overview, fracties_dict_input = fracties_dict)
        
        # update of table of attendance_per_party
        attendance_per_party_percentage_table = update_table_indices(attendance_per_party_percentage_df_formatted)
        
        # update graph of attendance_per_party
        attendance_per_party_percentage_graph = update_attendance_per_party_graph(attendance_per_party_percentage_df)
        
        
        return [f"Deze selectie resulteert in {amount_meetings_per_party} relevante vergaderingen.", # Use text formatting to allow easier build of layout
				attendance_per_party_percentage_table, 
				attendance_per_party_percentage_graph]

   
## Comment in integrated approach
# if __name__ == '__main__':
    # app.run_server(debug=True)
