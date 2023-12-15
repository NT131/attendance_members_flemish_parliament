import dash
from dash import dcc, html, dash_table # import dash_table to allow dynamically sorting tables
from dash.dependencies import Input, Output
import pandas as pd

from collections import defaultdict

# import plotly.graph_objs as go
# from plotly.subplots import make_subplots

import pandas as pd
from datetime import datetime
import pickle

import plotly.express as px # for scatterplots


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


dropdown_options_party  = [{"label": "Alle partijen", "value": "Alle partijen"}] + [{"label": party, "value": party} for party in fracties_dict.keys()] 

# Build app
app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)
app.title = "Aanwezigheid in commissies waarvan parlementsleden vast lid zijn" # title of tab in browser





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


# Create the layout
app.layout = html.Div(
    children=[
        # Header section
        html.Div(
            children=[
                # Title
                html.H1(
                    children="Aanwezigheid in commissies waarin parlementslid vast lid is",
                    className="header-title",
                    style={"color": "#FFFFFF"}
                ),
                # Description
                html.P(
                    children=(
                        "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?"
                        ),
                    className="header-description",
                    style={"color": "#FFFFFF"}
                ),
            ],
            className="section-header",
            style={"background-color": "#222222"} # Set dark background for this section
        ),
        # Selecting relevant data
        html.Div(
            children=[
                # Title
                html.H3(
                    "Selecteer de relevante partij en de periode.",
                    className="header-subsubtitle",
                ),
                # Dropdown to select party
                html.Div(
                    children=[
                        html.Div(
                            children="Welke partij?", 
                            className="menu-title"
                        ),
                        dcc.Dropdown(
                            id='party-dropdown',
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
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    # Graph of the average attendance per member
                    children=dcc.Graph(
                        id="member_amount_meetings_df_graph",
                    ),
                    className="card",
                ),
                # html.Div(
                # # Table of the attendance data for each member
                    # children=[
                        # html.H2(
                            # "Aanwezigheidsgegevens",
                            # className="header-title",
                            # style={"color": "#333333", "padding": "10px"} # ensure header has dark font since no dark background as in main title
                        # ),
                        # html.P(
                            # children=(
                                # "Hoeveel vergaderingen wonen parlementsleden bij van commissies waarvan ze vast lid zijn?"
                                # ),
                            # className="header-description",
                            # style={"color": "#333333"} # ensure header has dark font since no dark background as in main title
                        # ),
                    # ]
                # ),
                # html.Div(
                    # # Display the table
                    # children=html.Div(
                        # id="member_amount_meetings_df_table",
                        # className="dash_table"
                        # ),
                # ),
            ],
            className="wrapper",
        ),
    ]
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
    
    # print(filtered_df_overview)
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
    # Obtaining actual aggregated counts for how often permanent members were present
    aanwezig_per_lid = attendance_statistics.obtain_aggregated_counts(commissions_overview_df_input['aanwezig_count_vaste'])
    # Set member names as index (to allow easier processing later on)
    aanwezig_per_lid = aanwezig_per_lid.set_index("Member")

    # There seems to be some members present in `all_permanent_members` (which is based on `commissions_overview_df['vaste leden']`) that are not present in `aanwezig_per_lid` (which is based on `commissions_overview_df['aanwezig_count_vaste']`). We assess which these are, and add them to the `aanwezig_per_lid` dataframe, with count 0.
    # Obtain list of all members of parliament that reside in commissions as permanent member
    all_permanent_members = set()
    for member_list in commissions_overview_df_input['vaste leden']:
        all_permanent_members.update(member_list)
    # Obtain list of all members of parliament that do not reside in any commission as permanent member
    permanent_members_never_present = [element for element in all_permanent_members if element not in aanwezig_per_lid.index]
    # Add those members to the dataframe, with a count of 0
    for member in permanent_members_never_present:
        aanwezig_per_lid.loc[member] = 0
        
    #Create empty dataframe with permanent members, fill with zero (i.e. starting count) and use parmanent members as index
    member_amount_meetings_pd = pd.DataFrame(0, columns = ['Aantal relevante vergaderingen',
                                                           'Aantal vergaderingen aanwezig',
                                                           'Aantal vergaderingen afwezig',
                                                           'Aantal vergaderingen verontschuldigd',
                                                           'Percentage vergaderingen aanwezig',
                                                           'Aantal commissies waarin vast lid'],
                                            index = list(all_permanent_members))
    # Convert the percentage column to float to avoid later errors
    member_amount_meetings_pd['Percentage vergaderingen aanwezig'] = member_amount_meetings_pd['Percentage vergaderingen aanwezig'].astype(float)
    #Iterate over all permanent members of parliament
    for index_members, row_members in member_amount_meetings_pd.iterrows():
        # Iterate for each member through all commissions. 
        # If they are a permanent member, add the amount of meetings of that commission to their key in the dict
        for index_overview, row_overview in commissions_overview_df.iterrows():
            if index_members in row_overview["vaste leden"]:
                member_amount_meetings_pd.at[index_members, 'Aantal relevante vergaderingen'] += row_overview['aantal vergaderingen']
                
    
    #Iterate over all permanent members of parliament
    for index_members, row_members in member_amount_meetings_pd.iterrows():
        # Extract the aggregated count out of aanwezig_per_lid for the relevant member (i.e. serving as index) and add to member_amount_meetings_pd at relevant index
        verg_aanwezig = aanwezig_per_lid.loc[index_members, "Aggregated_Count"]
        member_amount_meetings_pd.at[index_members, "Aantal vergaderingen aanwezig"] = verg_aanwezig
        verg_afwezig = aanwezig_per_lid.loc[index_members, "Aggregated_Count"]
        member_amount_meetings_pd.at[index_members, "Aantal vergaderingen afwezig"] = verg_afwezig
        verg_verontschuldigd = aanwezig_per_lid.loc[index_members, "Aggregated_Count"]
        member_amount_meetings_pd.at[index_members, "Aantal vergaderingen verontschuldigd"] = verg_verontschuldigd
        
        # Obtain percentage of attended meetings (taking zero division into account, i.e. with Aantal relevante vergaderingen == 0)
        percentage_attendance = verg_aanwezig / row_members['Aantal relevante vergaderingen'] if row_members['Aantal relevante vergaderingen'] != 0 else 0.0      
        member_amount_meetings_pd.at[index_members, "Percentage vergaderingen aanwezig"] = percentage_attendance
    # Sort dataframe by percentage attended
    member_amount_meetings_pd = member_amount_meetings_pd.sort_values(by = "Percentage vergaderingen aanwezig", ascending = False)
    
    # Add parties of relevant members
    parties_list = []
    for member in member_amount_meetings_pd.index:
        party = attendance_statistics.find_member(fracties_dict_input, member)
        parties_list.append(party)       
    member_amount_meetings_pd["Partij"] = parties_list
    
    # Mapping members to the amount of commission they are permanent member of
    # using the grouped_by_count_dict obtained before
    member_amount_meetings_pd['Aantal commissies waarin vast lid'] = member_amount_meetings_pd.index.map(name2count_permanent_dict_input)
    
    
    return member_amount_meetings_pd


    

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

# Create scatter plot
def update_graph_scatter(df_input):
    hover_text = (
        df_input.apply(
            lambda row: (
                f"<b>{row.name}</b> was in de huidige periode <br>"
                f"op een totaal van {row['Aantal relevante vergaderingen']} vergaderingen <br>"
                f"{row['Aantal vergaderingen aanwezig']} keer aanwezig, "
                f"{row['Aantal vergaderingen afwezig']} keer afwezig en "
                f"{row['Aantal vergaderingen verontschuldigd']} keer verontschuldigd. <br>"
                f"Dat brengt het aanwezigheidspercentage op {row['Percentage vergaderingen aanwezig']:.1%}.<br><br>"
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
        # color=[
            # party_colors[value]
            # if not pd.isna(value)
            # else "#CCCCCC"
            # for value in df_input["Partij"].iloc
        # ],
        size="Aantal commissies waarin vast lid",
        custom_data=["Partij"],  # Include party name in custom data for hover label
        title="Aanwezigheid parlementsleden in commissies waarin ze vast lid zijn",
        color_discrete_map=party_colors,  # Define colors for parties
        # size_max=30,  # Adjust the maximum size of the bubbles
    )

    fig.update_traces(
        hovertemplate=(
            "%{customdata}<br><extra></extra>"
        ),
        customdata=hover_text,
    )
    
    print(df_input['Aantal commissies waarin vast lid'])
    
    return fig



# Update display
@app.callback(
    # [
        Output("member_amount_meetings_df_graph", "figure"),
        # Output("member_amount_meetings_df_table", "children")
    # ],
    [
        Input("party-dropdown", "value"),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')
    ]
)
def update_display(party_value, start_date, end_date):
    # Filter df based on party and timeframe
    filtered_df_overview, meetings_all_commissions_filtered_df = filter_data(
        start_date, end_date, party_value, commissions_overview_df, meetings_all_commissions_df
    )
    
    # Obtain dict on amount of commissions members are partaking
    name2count_permanent_dict = amount_commissions_as_permanent_dict(filtered_df_overview,
                                                                    parlementsleden_all_dict,fracties_dict)
    
    # Obtain aggregated counts of attendance (present, absent, absent with notice) for each member
    member_amount_meetings_df = obtain_attendance_permanent_members(filtered_df_overview, fracties_dict, name2count_permanent_dict)
    
    # Filter member_amount_meetings_df on selected party
    if party_value == "Alle partijen":
        member_amount_meetings_df_filtered = member_amount_meetings_df
    else:
        member_amount_meetings_df_filtered = member_amount_meetings_df[member_amount_meetings_df["Partij"] == party_value]
    
    # Turn attendance data in graph
    # member_amount_meetings_df_graph = update_graph_bar(member_amount_meetings_df_filtered) # bar graph
    member_amount_meetings_df_graph = update_graph_scatter(member_amount_meetings_df_filtered) # scatter graph
    
    # # Turn attendance data in dash table
    # member_amount_meetings_df_table = update_dash_table(member_amount_meetings_df_filtered, "member_amount_meetings_df_table")
    
    return member_amount_meetings_df_graph
    # , member_amount_meetings_df_table




# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
