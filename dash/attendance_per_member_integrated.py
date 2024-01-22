import dash
from dash import dcc, html, dash_table # import dash_table to allow dynamically sorting tables
from dash.dependencies import Input, Output
import pandas as pd

from collections import Counter, defaultdict

# import plotly.graph_objs as go
# from plotly.subplots import make_subplots

import pandas as pd
from datetime import datetime
import locale

import pickle

import plotly.express as px # for scatterplots


import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)

# Set the locale to Dutch (Belgian)
locale.setlocale(locale.LC_TIME, 'nl_BE.utf8')  # Set appropriate locale for Dutch


# Read in all meetings and attendance (both full (i.e. dict with party and id) and short (i.e. only name)
relevant_extraction_date = "2023-12-18"

meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df_{relevant_extraction_date}.pkl')
meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df_{relevant_extraction_date}.pkl')

# Obtain date of most recent meeting in dataset + format to e.g. "15 februari 2023"
date_most_recent_meeting_per_member = meetings_all_commissions_df['Datum vergadering'].max().strftime('%d %B %Y')

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
dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Create a default value for amount_meetings, i.e. relevant meetings
amount_meetings_per_member = len(meetings_all_commissions_df)  # Set amount of all meetings as default, it will be updated in the callback


## Comment in integrated approach
# # Build app
# app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)
# app.title = "Aanwezigheid in commissies waarvan parlementsleden vast lid zijn" # title of tab in browser





# Dictionary mapping parties to colors
# # Use colours obtained from website: manual insertion or reading in dict
party_colors = {'Groen': '#83de62',
    'Onafhankelijke': '#787878',
    'Vooruit': '#FF2900',
    'Vlaams Belang': '#ffe500',
    'cd&v': '#f5822a',
    'N-VA': '#ffac12',
    'Open Vld': '#003d6d',
    'PVDA': '#AA050E'
 }
# party_colors = pd.read_pickle("partij_kleur_dict.pkl")

## Comment in integrated approach
# app.
# Create the layout
layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Aanwezigheidsgegevens van parlementsleden per lid", className="header-subsubtitle"),
                html.P(
                    "Hoe vaak woonden leden vergaderingen van commissies bij, zowel als vast lid als als vervanger?",
                    className="header-description",
                ),
                html.Div(
                    children=[
                        html.Div("Welke partij?", className="menu-title"),
                        dcc.Dropdown(
                            id='party-dropdown-per-member',
                            options=dropdown_options_party,
                            value="Alle partijen", # default value
                            clearable=False,
                            className="dropdown",
                        ),
                    ],
                    className="menu-element" 
                ),
                html.Div(
                    children=[
                        html.Div(
							"Relevante periode", 
							className="menu-title"
						),
						html.Div(
							# Display the most recent meeting date
							id='most-recent-date-per-member',
							children=f"Laatste update: {date_most_recent_meeting_per_member}",
							style={'font-style': 'italic'}
						),
						dcc.DatePickerRange(
                            id="date-range-per-member",
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
						html.Div(id='amount_meetings_per_member',
								 children=f"Deze selectie resulteert in {amount_meetings_per_member} relevante vergaderingen."), 
					],
					className="menu-element"
				),
			],
            className="section-header",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Gemiddelde aanwezigheid per lid in vaste commisises", className="header-subsubtitle"),
                        html.P(
                            "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?",
                            className="header-description",
                        ),
                    ],
                    className="section-header",
                ),
                html.Div(
                    children=dcc.Graph(id="permanent_member_amount_meetings_df_graph"),
                    className="card",
                ),
            ],
            className="wrapper",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Gemiddelde aanwezigheid per lid in commissies waar ze geen vast lid zijn", className="header-subsubtitle"),
                        html.P(
                            "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze geen vast lid zijn?",
                            className="header-description",
                        ),
                    ],
                    className="section-header",
                ),
                html.Div(
                    children=dcc.Graph(id="non_permanent_member_amount_meetings_df_graph"),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ],
    # use CSS flexbox approach to easily structure graphs and titles
    style={"display": "flex", "flex-direction": "column"}
)


# Define function to filter data based on user selection
def filter_data(start_date, end_date, party_value, 
commissions_overview_df_input, meetings_all_commissions_df_input):   
    # Ensure correct date format
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    # Filter DataFrame with all commission meetings based on the date range
    meetings_all_commissions_filtered_df = meetings_all_commissions_df_input[
        (meetings_all_commissions_df_input['Datum vergadering'] >= start_date) &
        (meetings_all_commissions_df_input['Datum vergadering'] <= end_date)
    ]
    
    
    # Obtain for the filtered df the attendance statistics using imported function
    filtered_df_overview = attendance_statistics.obtain_attendance_statistics(
    commissions_overview_df_input = commissions_overview_df_input, 
    meetings_all_commissions_df_input = meetings_all_commissions_filtered_df
    )
    
    return (filtered_df_overview, meetings_all_commissions_filtered_df)


def amount_commissions_as_permanent_dict(commissions_overview_df_input, 
                                    parlementsleden_all_dict_input, 
                                    fracties_dict_input):
    """
    Function to obtain dict of how many commissions each member of parliament is a permanent member of.
    {'Willem-Frederik Schiltz': 12,
     'Chris Janssens': 10,
     'Peter Van Rompuy': 9,
     "Jos D'Haese": 9,
     'Andries Gryffroy': 7,
     ...}
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
    
    # Turn into dict that maps names to amount of commissions
    name2amount_dict = {}
    for number, names in grouped_by_count.items():
        for name in names:
            name2amount_dict[name] = number
    
    return name2amount_dict

def obtain_attendance_permanent_members(commissions_overview_df_input, fracties_dict_input, name2count_permanent_dict_input):
    """
    We obtain aggregated counts per member over all commissions, to get overall totals per member how often they had a certain attendance status (e.g. 'Aanwezig', 'Afwezig', 'Verontschuldigd'), using a helper function `obtain_aggregated_counts()`.
    """
    # Obtaining actual aggregated counts for how often permanent members were present / absent / absent with notice + rename output column 'Aggregate_Count" to more insightful name + to avoid duplicates)
    aanwezig_per_lid = attendance_statistics.obtain_aggregated_counts(commissions_overview_df_input['aanwezig_count_vaste']).rename(columns={"Aggregated_Count": "Aantal vergaderingen aanwezig"})
    afezig_per_lid = attendance_statistics.obtain_aggregated_counts(commissions_overview_df_input['afwezig_count_vaste']).rename(columns={"Aggregated_Count": "Aantal vergaderingen afwezig"})
    verontschuldigd_per_lid = attendance_statistics.obtain_aggregated_counts(commissions_overview_df_input['verontschuldigd_count_vaste']).rename(columns={"Aggregated_Count": "Aantal vergaderingen verontschuldigd"})
    #Merge those dfs, using 'Member' column as identifier
    merged_df = pd.merge(aanwezig_per_lid, afezig_per_lid,  on="Member", how="outer")
    merged_df = pd.merge(merged_df, verontschuldigd_per_lid,  on="Member", how="outer") 
    # Set member names as index (to allow easier processing later on)
    aanwezigheid_per_lid_df = merged_df.set_index("Member")

    # There seems to be some members present in `all_permanent_members` (which is based on `commissions_overview_df['vaste leden']`) that are not present in `aanwezig_per_lid` (which is based on `commissions_overview_df['aanwezig_count_vaste']`). We assess which these are, and add them to the `aanwezig_per_lid` dataframe, with count 0.
    # Obtain list of all members of parliament that reside in commissions as permanent member
    all_permanent_members = set()
    for member_list in commissions_overview_df_input['vaste leden']:
        all_permanent_members.update(member_list)
    # Obtain list of all members of parliament that do not reside in any commission as permanent member
    permanent_members_never_present = [element for element in all_permanent_members if element not in aanwezigheid_per_lid_df.index]
    # Add those members to the dataframe, with counts of 0
    for member in permanent_members_never_present:
        aanwezigheid_per_lid_df.loc[member] = 0
        
    #Add extra columns for amount of relevant meetings, percentage and amount commissions as permanent member
    aanwezigheid_per_lid_df['Aantal relevante vergaderingen'] = 0
    aanwezigheid_per_lid_df['Percentage vergaderingen aanwezig'] = 0.0 # initialise as float
    aanwezigheid_per_lid_df['Aantal commissies waarin vast lid'] = 0
    #Fill amount of relevant meetings: Iterate over all permanent members of parliament
    for index_members, row_members in aanwezigheid_per_lid_df.iterrows():
        # Iterate for each member through all commissions. 
        # If they are a permanent member, add the amount of meetings of that commission to their key in the dict
        for index_overview, row_overview in commissions_overview_df.iterrows():
            if index_members in row_overview["vaste leden"]:
                aanwezigheid_per_lid_df.at[index_members, 'Aantal relevante vergaderingen'] += row_overview['aantal vergaderingen']
        
                
    
    #Iterate over all permanent members of parliament
    for index_members, row_members in aanwezigheid_per_lid_df.iterrows():
        # Obtain percentage of attended meetings (taking zero division into account, i.e. with Aantal relevante vergaderingen == 0)
        percentage_attendance = row_members['Aantal vergaderingen aanwezig'] / row_members['Aantal relevante vergaderingen'] if row_members['Aantal relevante vergaderingen'] != 0 else 0.0      
        aanwezigheid_per_lid_df.at[index_members, "Percentage vergaderingen aanwezig"] = percentage_attendance

    # Sort dataframe by percentage attended
    aanwezigheid_per_lid_df = aanwezigheid_per_lid_df.sort_values(by = "Percentage vergaderingen aanwezig", ascending = False)
    
    # Add parties of relevant members
    parties_list = []
    for member in aanwezigheid_per_lid_df.index:
        party = attendance_statistics.find_member(fracties_dict_input, member)
        parties_list.append(party)       
    aanwezigheid_per_lid_df["Partij"] = parties_list
    
    # Mapping members to the amount of commission they are permanent member of
    # using the grouped_by_count_dict obtained before
    aanwezigheid_per_lid_df['Aantal commissies waarin vast lid'] = aanwezigheid_per_lid_df.index.map(name2count_permanent_dict_input)
    
    
    return aanwezigheid_per_lid_df


def obtain_attendance_non_permanent_members(commissions_overview_df_input, 
                                            parlementsleden_all_dict_input,
                                            fracties_dict_input):
    """
    We obtain aggregated counts per member over all commissions in which they
    were no permanent member, to get overall totals per member how often they
    had a certain attendance     status (e.g. 'Aanwezig', 'Afwezig', 'Verontschuldigd'), 
    using a helper function `obtain_aggregated_counts()`.
    """
    # Obtaining actual aggregated counts for how often members were present
    aanwezig_per_lid_alle = attendance_statistics.obtain_aggregated_counts(commissions_overview_df_input['aanwezig_count_alle'])
    # Set member names as index (to allow easier processing later on)
    aanwezig_per_lid_alle = aanwezig_per_lid_alle.set_index("Member")
    
    
    # Then we obtain a list of all members of parliament, to compare them with the attendance data.
    alle_parlementsleden_list = [parlementsleden_all_dict_input[member_tuple][0] for member_tuple in parlementsleden_all_dict_input.keys()]
    
    
    # Obtain list of all members of parliament that have never attended a commission
    all_members_never_present = [element for element in alle_parlementsleden_list if element not in aanwezig_per_lid_alle.index]

    
    # Then we obtain for each commission a list of members that have attended meetings of that commission although they are no permanent member of that commission.
    members_present_but_no_permanent_overall = [] # Create empty list to fill
    # Iterate over each commission
    for index_overview, row_overview in commissions_overview_df_input.iterrows():
        permanent_members = row_overview["vaste leden"] # Obtain permanent members of commission
        # Obtain list of all members that have been present at at least 1 meeting of this commission
        members_present_in_meetings = [member_tuple[0] for member_tuple in row_overview["aanwezig_count_alle"]]
        # Obtain subset of those members that are no permanent members
        members_present_but_no_permanent = [member for member in members_present_in_meetings if member not in permanent_members]
        # Append this subset to the overall list
        members_present_but_no_permanent_overall.append(members_present_but_no_permanent)
      
    
    # Then we obtain for each of those non-permanent members how often they were present at a specific commission.
    count_members_present_but_not_permanent_overall = []
    for index, spec_commission_attendance_list in enumerate(commissions_overview_df_input['aanwezig_count_alle']):
        count_members_present_but_not_permanent = [member_tuple for member_tuple in spec_commission_attendance_list if member_tuple[0] in members_present_but_no_permanent_overall[index]]
        count_members_present_but_not_permanent_overall.append(count_members_present_but_not_permanent)
    # Append resulting list as new column to overview data frame 
    commissions_overview_df_input["aanwezig_count_alle_maar_geen_vast_lid"] = count_members_present_but_not_permanent_overall
        
        
    # Obtaining actual aggregated counts for how often members were present
    aanwezig_per_lid_alle_maar_niet_vast_df = attendance_statistics.obtain_aggregated_counts(count_members_present_but_not_permanent_overall)
    # Use member name as index
    aanwezig_per_lid_alle_maar_niet_vast_df = aanwezig_per_lid_alle_maar_niet_vast_df.set_index('Member')

    
    # Then we add the party the dataframe, using the earlier defined helper function.
    parties_list = []
    for member in aanwezig_per_lid_alle_maar_niet_vast_df.index:
        party = attendance_statistics.find_member(fracties_dict_input, member)
        parties_list.append(party)
    aanwezig_per_lid_alle_maar_niet_vast_df["Partij"] = parties_list
    
    
    # We also add in how many additional commissions they were present.
    aanwezig_per_lid_alle_maar_niet_vast_df["Aantal commissies extra aanwezig"] = 0
    # Flatten list of attendance (including counts)
    flattened_attendance_list = [item for sublist in commissions_overview_df_input["aanwezig_count_alle_maar_geen_vast_lid"] for item in sublist]
    # Maintain only names and not counts
    flattened_attendance_list = [item[0] for item in flattened_attendance_list]
    # Count occurrences of members for all meetings represented in attandance_list
    amount_of_meetings_counter = Counter(flattened_attendance_list)
    # Sort elements by their counts in descending order
    amount_of_meetings_list = sorted(amount_of_meetings_counter.items(), key=lambda x: x[1], reverse=True)
    for member_name, count in amount_of_meetings_counter.items():
        aanwezig_per_lid_alle_maar_niet_vast_df.at[member_name, "Aantal commissies extra aanwezig"] = count
    
    
    # Finally we also add for each member in how many commissions they are a permanent member.
    aanwezig_per_lid_alle_maar_niet_vast_df["Aantal commissies waarin vast lid"] = 0 # Initialize new column
    # Create flattened list of all permanent member accross all commissions
    flattened_permanent_members = [item for sublist in commissions_overview_df_input['vaste leden'] for item in sublist]
    # Count occurrences of meetings for which member is permanent member
    amount_of_meetings_as_permanent_counter = Counter(flattened_permanent_members)
    #Store counts in column '"Aantal commissies waarin vast lid"'
    for member_name, count in amount_of_meetings_as_permanent_counter.items():
        if member_name in aanwezig_per_lid_alle_maar_niet_vast_df.index:
            aanwezig_per_lid_alle_maar_niet_vast_df.at[member_name, "Aantal commissies waarin vast lid"] = count


    # Rename column "Aggregated_Count" to "Aantal vergaderingen aanwezig"
    aanwezig_per_lid_alle_maar_niet_vast_df = aanwezig_per_lid_alle_maar_niet_vast_df.rename(columns={"Aggregated_Count": "Aantal vergaderingen aanwezig"})
    
    
    return aanwezig_per_lid_alle_maar_niet_vast_df
    

def update_dash_table(df, set_id: str):
    #Create copy and modify percentage formatting of this
    df_copy = df.copy()
    df_copy['Percentage vergaderingen aanwezig'] = df_copy['Percentage vergaderingen aanwezig'].apply(lambda x: f'{x:.1%}')
    
    # Reset index and rename the 'index' column to 'Parlementsleden'
    df_copy = df_copy.reset_index()  # Reset index
    df_copy = df_copy.rename(columns={'index': 'Parlementsleden'})
    
    table = dash_table.DataTable(
        id=set_id,
        columns=[{'name': col, 'id': col} for col in df_copy.columns],  # Use columns of dataframe as table columns
        data=df_copy.to_dict('records'),  # Use dataframe records to populate data
        sort_action='native',  # Enable sorting
        style_table={'overflowX': 'auto'},  # Enable horizontal scroll
    )

    return table


def update_graph_bar(df_input):

    df_sorted = df_input.sort_values(by="Percentage vergaderingen aanwezig", ascending=False)  # Sort by aggregate count

    figure = {
        "data": [
            {
                "x": df_sorted.index,
                "y": df_sorted["Percentage vergaderingen aanwezig"],
                "type": "bar",
                "marker": {"color": [party_colors.get(party, "grey") for party in df_sorted['Partij']]},
                "hovertemplate": "<b>%{x}</b><br>"
                                 "Partij: %{text[0]}<br>"
                                 "Aantal relevante vergaderingen: %{text[1]}<br>"
                                 "Aantal bijgewoonde vergaderingen: %{text[2]}<br>"
                                 "Percentage vergaderingen aanwezig: %{text[3]:.1%}<extra></extra>",
                "text": df_sorted[['Partij', 'Aantal relevante vergaderingen', 'Aantal bijgewoonde vergaderingen', 'Percentage vergaderingen aanwezig']].values.tolist(),
            }
        ],
        "layout": {
            "title": "Aanwezigheid van parlementsleden in commissies waarvan ze vast lid zijn",
            "xaxis": {"title": "Parlementslid", "tickangle": -45, "tickfont": {"size": 10}, "automargin": True},
            "yaxis": {"title": "Percentage vergaderingen aanwezig"},
        },
    }

    return figure



# Create scatter plot for permanent members
def update_graph_scatter_permanent(df_input):
    hover_text = (
        df_input.apply(
            lambda row: (
                f"<b>{row.name}</b> was in de huidige periode <br>"
                f"op een totaal van {row['Aantal relevante vergaderingen']} vergaderingen <br>"
                f"{int(row['Aantal vergaderingen aanwezig']) if not pd.isnull(row['Aantal vergaderingen aanwezig']) else '<i>N/A</i>'} keer aanwezig, "
                f"{int(row['Aantal vergaderingen afwezig']) if not pd.isnull(row['Aantal vergaderingen afwezig']) else '<i>N/A</i>'} keer afwezig en "
                f"{int(row['Aantal vergaderingen verontschuldigd']) if not pd.isnull(row['Aantal vergaderingen verontschuldigd']) else '<i>N/A</i>'} keer verontschuldigd. <br>"
                f"Dat brengt het aanwezigheidspercentage op <b>{row['Percentage vergaderingen aanwezig']:.1%}</b>.<br><br>"
                f"Zetelt als vast lid in {row['Aantal commissies waarin vast lid']} commissie(s)."
            ),
            axis=1,
        )
    )

    fig = px.scatter(
        df_input,
        x="Percentage vergaderingen aanwezig",
        y="Partij",
        color='Partij',
        size="Aantal commissies waarin vast lid",
        custom_data=["Partij"],  # Include party name in custom data for hover label
        title="Aanwezigheid parlementsleden in commissies waarin ze vast lid zijn",
        color_discrete_map=party_colors,  # Define colors for parties
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata}</b><br>"
        ),
        customdata=hover_text,
    )
    
    fig.update_layout(
        xaxis=dict(
            tickformat=".0%",  # Format y-axis as percentage without decimal
            title="Percentage vergaderingen aanwezig",
        ),
        # hovermode='closest',  # Set hovermode to 'closest'
    )
    
    return fig



# Create scatter plot for non-permanent members
def update_graph_scatter_non_permanent(df_input):
    hover_text = (
        df_input.apply(
            lambda row: (
                f"<b>{row.name}</b> was in de huidige periode <b> {row['Aantal vergaderingen aanwezig']}</b> keer aanwezig <br>"
                f"op vergaderingen van commissies waarvan deze geen vast lid is. <br><br>"
                f"Zetelt als vast lid in {row['Aantal commissies waarin vast lid']} commissie(s)."
            ),
            axis=1,
        )
    )

    fig = px.scatter(
        df_input,
        x="Aantal vergaderingen aanwezig",
        y="Partij",
        color='Partij',
        # color=[
            # party_colors[value]
            # if not pd.isna(value)
            # else "#CCCCCC"
            # for value in df_input["Partij"].iloc
        # ],
        size="Aantal commissies waarin vast lid",
        custom_data=["Partij"],  # Include party name in custom data for hover label
        title="Aanwezigheid parlementsleden in commissies waarin ze geen vast lid zijn",
        color_discrete_map=party_colors,  # Define colors for parties
        # size_max=30,  # Adjust the maximum size of the bubbles
    )

    fig.update_traces(
        hovertemplate=(
            "%{customdata}<br><extra></extra>"
        ),
        customdata=hover_text,
    )
    
    
    return fig

#Create function to load app in integrated appraoch
def register_callbacks(app):

    # Update display
    @app.callback(
        [
			Output('amount_meetings_per_member', 'children'),
            Output("permanent_member_amount_meetings_df_graph", "figure"),
            Output("non_permanent_member_amount_meetings_df_graph", "figure"),
            # Output("member_amount_meetings_df_table", "children")
        ],
        [
            Input("party-dropdown-per-member", "value"),
            Input('date-range-per-member', 'start_date'),
            Input('date-range-per-member', 'end_date')
        ]
    )
    def update_display(party_value, start_date, end_date):
        # Filter df based on party and timeframe
        filtered_df_overview, meetings_all_commissions_filtered_df = filter_data(
            start_date, end_date, party_value, commissions_overview_df, meetings_all_commissions_df
        )
        
		# Obtain count of relevant data, after filtering
        amount_meetings_per_member = len(meetings_all_commissions_filtered_df)
		
        # Obtain dict on amount of commissions members are partaking
        name2count_permanent_dict = amount_commissions_as_permanent_dict(filtered_df_overview,
                                                                        parlementsleden_all_dict,fracties_dict)
        
        # Obtain aggregated counts of attendance (present, absent, absent with notice) for each permanent member
        permanent_member_amount_meetings_df = obtain_attendance_permanent_members(filtered_df_overview, fracties_dict, name2count_permanent_dict)
        
        non_permanent_member_amount_meetings_df = obtain_attendance_non_permanent_members(
                filtered_df_overview, parlementsleden_all_dict, fracties_dict)
        
        # Filter permanent_member_amount_meetings_df & non_permanent_member_amount_meetings_df on selected party
        if party_value == "Alle partijen":
            permanent_member_amount_meetings_df = permanent_member_amount_meetings_df
            non_permanent_member_amount_meetings_df = non_permanent_member_amount_meetings_df
            
        else:
            permanent_member_amount_meetings_df = permanent_member_amount_meetings_df[permanent_member_amount_meetings_df["Partij"] == party_value]
            non_permanent_member_amount_meetings_df = non_permanent_member_amount_meetings_df[non_permanent_member_amount_meetings_df["Partij"] == party_value]
        
        # Turn attendance data in graph
        # permanent_member_amount_meetings_df_graph = update_graph_bar(permanent_member_amount_meetings_df) # bar graph
        permanent_member_amount_meetings_df_graph = update_graph_scatter_permanent(permanent_member_amount_meetings_df) # scatter graph
        
        # non_permanent_member_amount_meetings_df_graph = update_graph_bar(non_permanent_member_amount_meetings_df) # bar graph
        non_permanent_member_amount_meetings_df_graph = update_graph_scatter_non_permanent(non_permanent_member_amount_meetings_df) # scatter graph
        
        # # Turn attendance data in dash table
        # permanent_member_amount_meetings_df_table = update_dash_table(permanent_member_amount_meetings_df, "permanent_member_amount_meetings_df_table")
        # member_amount_meetings_df_table = update_dash_table(non_permanent_member_amount_meetings_df_graph, "non_permanent_member_amount_meetings_df_table")
        
        return [f"Deze selectie resulteert in {amount_meetings_per_member} relevante vergaderingen.", # Use text formatting to allow easier build of layout
				permanent_member_amount_meetings_df_graph, 
				non_permanent_member_amount_meetings_df_graph]
        # , member_amount_meetings_df_table



## Comment in integrated approach
# # Run the app
# if __name__ == "__main__":
    # app.run_server(debug=True)
