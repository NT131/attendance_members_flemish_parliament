import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table

try:
    import dash_bootstrap_components as dbc #to use .Col feature for displaying multiple pie charts
except:
    print('dash_bootstrap_components package not installed')

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from collections import Counter

import pandas as pd

from datetime import datetime
import locale

import pickle

import attendance_statistics # import functions of attendance_statistics.py (i.e. obtain_attendance_statistics() and helper functions)

# Set the locale to Dutch (Belgian)
locale.setlocale(locale.LC_TIME, 'nl_BE.utf8')  # Set appropriate locale for Dutch


# # Read in all meetings and attendance (both full (i.e. dict with party and id) and short (i.e. only name)
# relevant_extraction_date = "2023-12-18"

#meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df_{relevant_extraction_date}.pkl')
#meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df_{relevant_extraction_date}.pkl')
meetings_all_commissions_df = pd.read_pickle(f'../data/meetings_all_commissions_df.pkl')
meetings_all_commissions_short_df = pd.read_pickle(f'../data/meetings_all_commissions_short_df.pkl')


# Obtain date of most recent meeting in dataset + format to e.g. "15 februari 2023"
date_most_recent_meeting_per_com = meetings_all_commissions_df['Datum vergadering'].max().strftime('%d %B %Y')

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
amount_meetings_per_com = len(meetings_all_commissions_df)  # Set amount of all meetings as default, it will be updated in the callback


# Uncomment in integrated approach
# # Build app
# app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)

# Create a container to hold the pie charts
# graphs_container = dbc.Col()
# graphs_container = html.Div(id='graphs_container')



# Create the layout
## Comment in integrated approach
# app.


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
								html.Div(
									# Display the most recent meeting date
									id='most-recent-date-per-com',
									children=f"Laatste update: {date_most_recent_meeting_per_com}",
									style={'font-style': 'italic'}
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
						# Display impact of data selection (i.e. how many meetings are taken into account)	
						html.Div(
							children=[
								html.Div(id='amount_meetings_per_com',
										 children=f"Deze selectie resulteert in {amount_meetings_per_com} relevante vergaderingen."), 
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
                        html.Div(
                            # Wrapper for both graph and table
                            children=[
                                # Graph attendance per commission
                                html.Div(
                                    children=[
                                        html.Div(id='graphs_container'),  # Pie chart container
                                        html.Div(id='dummy-trigger', style={'display': 'none'})  # Dummy component for update
                                    ],
                                    className="graph-title",
                                ),
                                # Table attendance_per_commission
                                # html.Div(
                                #     className="table-container",
                                #     children=[
                                #         html.Div(
                                #             # Display the table_attendance
                                #             id='table_attendance',
                                #             # className="dash-table",
                                #             style_table={'overflowX': 'auto'},
                                #             # style_cell={
                                #             #     'fontFamily': 'Lato, sans-serif',
                                #             #     'fontSize': 14,
                                #             #     'textAlign': 'left',
                                #             #     'minWidth': '150px',
                                #             #     'whiteSpace': 'normal',
                                #             #     'textOverflow': 'ellipsis',
                                #             # },
                                #             style_header={
                                #                 'fontWeight': 'bold',
                                #                 'fontSize': 16,
                                #             },
                                #             className="custom-datatable-container",
                                #             children=html.P("Tabel niet beschikbaar", style={"color": "red"})
                                #         ),
                                #     ]
                                # ),
                                
                                # Table attendance_per_commission
                                html.Div(
                                    className="table-container",
                                    children=[
                                        dash_table.DataTable(
                                            id='table_attendance',
                                            # Rename columns in view
                                            columns=[
                                                {'name': 'Parlementslid', 'id': 'Naam vast lid'},
                                                {'name': 'Vergaderingen aanwezig', 'id': 'Aantal keer aanwezig'},
                                            ],
                                            style_table={'overflowX': 'auto'},
                                            style_cell={
                                                'fontFamily': 'Lato, sans-serif',
                                                'fontSize': 14,
                                                'textAlign': 'left',
                                                'minWidth': '150px',
                                                'whiteSpace': 'normal',
                                                'textOverflow': 'ellipsis',
                                            },
                                            style_header={
                                                'fontWeight': 'bold',
                                                'fontSize': 16,
                                            },
                                            # Allow sorting of columns
                                            sort_action='native',  # Enable sorting
                                            sort_mode='multi',  # Allow multiple column sorting
                                            sort_by=[{'column_id': 'Aantal keer aanwezig', 'direction': 'desc'}],  # Default sorting column and orientation
                                        ),
                                    ]
                                ),
                            ],
                            style={"display": "flex", "flex-direction": "row"} # Set flexbox layout for row dispay to allow table and graph next to each other     
                        ),          
                    ],
                    className="wrapper",
                ),
            ],
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
            data_present = row['Gemiddelde aantal aanwezig vaste leden (afgerond)']
            data_absent = row['Gemiddelde aantal afwezig vaste leden (afgerond)']
            data_excused = row['Gemiddelde aantal verontschuldigd vaste leden (afgerond)']

            if not pd.isnull(data_present) and not pd.isnull(data_absent) and not pd.isnull(data_excused):
                labels = ['aanwezig', 'afwezig', 'verontschuldigd']
                sizes = [data_present, data_absent, data_excused]
                colors = ['green', 'red', 'orange']

                # Create a custom hovertemplate without mentioning 'trace 0'
                hovertemplate = "<b>aantal leden</b>: %{value}"

                # Create the Pie chart directly with the custom hovertemplate
                pie_chart = go.Pie(
                    labels=labels,
                    values=sizes,
                    textinfo='percent',  # Display percentages by default
                    hoverinfo='label+percent+value',  # Include necessary hover information
                    hovertemplate=hovertemplate,  # Define hover template
                    hole=0.3,
                    marker=dict(colors=colors)
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

    return graphs




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

    # table = dash_table.DataTable(
    #     id='written-questions-table',
    #     data=df,
    #     # columns=[
    #     #     {'name': 'Parlementslid', 'id': 'Naam vast lid'},
    #     #     {'name': 'Bevoegde minister', 'id': 'minister'},
    #     #     # use markdown represention to leverage clickable links of df
    #     #     {'name': 'Onderwerp', 'id': 'onderwerp', 'presentation': 'markdown'}, 
    #     # ],
    #     # page_size=25, #  Set the number of rows per page
    #     style_table={'overflowX': 'auto'},
    #     style_cell={
    #         'fontFamily': 'Lato, sans-serif',
    #         'fontSize': 14,
    #         'textAlign': 'left',
    #         'minWidth': '150px',
    #         'whiteSpace': 'normal',
    #         'textOverflow': 'ellipsis',
    #     },
    #     style_header={
    #         'fontWeight': 'bold',
    #         'fontSize': 16,
    #     },
    # )
    
    return table


def update_dash_table(df):

    datatable = dash_table.DataTable(data=df.to_dict('records'))
    
    

    return datatable  # Return a list containing the table element

#Create function to load app in integrated appraoch
def register_callbacks(app):

    # Define callback to update display based on selected commission and date range
    @app.callback(
        [
		Output('amount_meetings_per_com', 'children'),
		Output('graphs_container', 'children'),
        # Output('table_attendance', 'children'),
        Output('table_attendance', 'data'),
		],
        [Input('commissie-dropdown-per-com', 'value'),
         Input('date-range-per-com', 'start_date'),
         Input('date-range-per-com', 'end_date')]
    )
    def update_display(commission_value, start_date, end_date):
        # Filter df based on user input
        filtered_df_overview, filtered_df_meetings = filter_data(
        start_date, end_date, commission_value,
        commissions_overview_df, meetings_all_commissions_df)
        
		# Obtain count of relevant data, after filtering
        amount_meetings_per_com = len(filtered_df_meetings)
        
        # Obtain table including the attendance counts of the permanent members, 
        # using the Counter objects in the column 'aanwezig_count_vaste' of filtered_df_overview
        attendance_permanent_df = attendance_statistics.obtain_counter_from_list_counter_likes(
            filtered_df_overview['aanwezig_count_vaste'], ['Naam vast lid', 'Aantal keer aanwezig'])
    
        # Generate htlm table
            # Option 1: use normal table
        # table_attendance = update_table(attendance_permanent_df) 
            # Option 2: use dash_table
        # table_attendance = update_dash_table(attendance_permanent_df)
        table_attendance = attendance_permanent_df.to_dict('records')

    	# Update the pie charts based on the selected data
        pie_charts = update_pie_charts(filtered_df_overview)
        
        return [f"Deze selectie resulteert in {amount_meetings_per_com} relevante vergaderingen.", # Use text formatting to allow easier build of layout
				pie_charts,  # Return the list of graphs as children of graphs_container
                table_attendance
			   ]
       
    
# Comment in integrated approach   
# if __name__ == '__main__':
    # app.run_server(debug=True)
