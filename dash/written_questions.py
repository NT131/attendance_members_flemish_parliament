# =============================================================================
# Setting up
# =============================================================================

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

import pickle

from attendance_statistics import get_party

# =============================================================================
# Reading in relevant support data
# =============================================================================
# Load df with written questions and information about parties
written_questions_df = pd.read_pickle('../data/details_questions_term_df.pkl')
# Create a default value for amount_meetings, i.e. relevant meetings
amount_questions = len(written_questions_df)  # Set amount of all meetings as default, it will be updated in the callback

# Load information about parties
with open('../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)



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

# Map ministers to their party colors
minister_colors = {
    'Benjamin Dalle': '#f5822a',
    'Hilde Crevits': '#f5822a',
    'Jo Broens': '#f5822a',
    'Wouter Beke': '#f5822a',
    
    'Ben Weyts': '#ffac12',
    'Jan Jambon': '#ffac12',
    'Matthias Diependaele': '#ffac12',
    'Zuhal Demir': '#ffac12',
    
    'Bart Somers': '#003d6d',
    'Gwendolyne Rutten': '#003d6d',
    'Lydia Peeters': '#003d6d',
 }

# =============================================================================
# # Initiate dash app
# =============================================================================

# Comment out in integrated approach
# # Dash app
# app = dash.Dash(__name__,
#                 assets_folder='assets') # Relative path to the folder of css file))

# =============================================================================
# Dash layout
# =============================================================================

## Comment in integrated approach
# app.
layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Schriftelijke vragen",
                        className="header-subsubtitle"),
                html.P("Welke parlementsleden stelden het meeste parlementaire vragen? En welke ministers kregen de meeste vragen te verwerken?",
                       className="header-description"),
            ],
            className="section-header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(
                            "Selecteer de relevante periode.",
                            className="header-subsubtitle",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children="Relevante periode", 
                                    className="menu-title"
                                ),
                    				# html.Div(
                    				# 	# Display the most recent meeting date
                    				# 	id='most-recent-date-per-party',
                    				# 	children=f"Laatste update: {date_most_recent_meeting_per_party}",
                    				# 	style={'font-style': 'italic'}
                    				# ),
                                dcc.DatePickerRange(
                                    id="date-range-written-questions",
                                    min_date_allowed=written_questions_df["datum beantwoord"].min(),
                                    max_date_allowed=written_questions_df["datum beantwoord"].max(),
                                    start_date=written_questions_df["datum beantwoord"].min(),
                                    end_date=written_questions_df["datum beantwoord"].max(),
                                    display_format='DD/MM/YYYY',  # Set the display format to 'dd/mm/yyyy' instead of default 'mm/dd/yyyy'
                                ),
                            ],
                            className="menu-element"
                        ),
                    		# Display impact of data selection (i.e. how many written questions are taken into account)	
                    		html.Div(
                    			children=[
                    				html.Div(id='amount_questions',
                    						 children=f"Deze selectie resulteert in {amount_questions} schriftelijke vragen."),
                    			],
                    			className="menu-element"
                    		),
                    ], 
                    className="section-chart",
                ),
            ],
            className="wrapper",
        ),
    
        dcc.Dropdown(
            id='x-axis-dropdown',
            options=[
                {'label': 'Vraagsteller', 'value': 'vraagsteller'},
                {'label': 'Partij', 'value': 'partij'},
                {'label': 'Minister', 'value': 'minister'},
                {'label': 'Thema', 'value': 'thema'},
            ],
            value='vraagsteller', # Default value
            style={'width': '50%'}
        ),
        dcc.Graph(id='written_questions_graph'),
    ],
    # use CSS flexbox approach to easily structure graphs and titles
    style={"display": "flex", "flex-direction": "column"} 
)



# =============================================================================
# Callback
# =============================================================================
#Define function to filter data based on user selection
def filter_data(start_date, end_date, written_questions_df):   
    # Ensure correct date format
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    
    
    # Filter DataFrame with all commission meetings further based on the date range
    written_questions_filtered_df = written_questions_df[
         (written_questions_df['datum beantwoord'] >= start_date) &
         (written_questions_df['datum beantwoord'] <= end_date)
     ]
    
    return written_questions_filtered_df


def update_chart(selected_axis, written_questions_df_input):
  
    if selected_axis == 'vraagsteller':      
        # Create a DataFrame with member, count, and party columns
        grouped_data = written_questions_df_input['vraagsteller'].value_counts().reset_index()
        grouped_data.columns = ['Parlementslid', 'Aantal vragen']

        # Apply function to create a new column 'Partij' based on fracties_dict
        grouped_data['Partij'] = grouped_data.apply(get_party, axis=1,
                                                    facties_dict_input=fracties_dict)

        fig = px.bar(grouped_data,
                     x='Parlementslid',
                     y='Aantal vragen',
                     color='Partij',
                     color_discrete_map=party_colors,
                     labels={'x': 'Parlementslid', 'y': 'Aantal vragen'},
                     title='Vragen per parlementslid')
        
        # Update x-axis to reflect the sorted order
        fig.update_xaxes(categoryorder='total descending')

    elif selected_axis == 'minister':
        grouped_data = written_questions_df_input['minister'].value_counts().reset_index()
        grouped_data.columns = ['Minister', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Minister',
                     y='Aantal vragen',
                     color='Minister',
                     color_discrete_map=minister_colors,
                     labels={'x': 'Minister', 'y': 'Aantal vragen'},
                     title='Vragen aan ministers')

    elif selected_axis == 'partij':

        grouped_data = written_questions_df_input['vraagsteller_partij'].value_counts().reset_index()
        grouped_data.columns = ['Partij', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Partij',
                     y='Aantal vragen',
                     color='Partij',
                     color_discrete_map=party_colors,
                     labels={'x': 'Partij', 'y': 'Aantal vragen'},
                     title='Vragen gesteld per partij')
        
    elif selected_axis == 'thema':
        grouped_data = written_questions_df_input['thema'].value_counts().reset_index()
        grouped_data.columns = ['Thema', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Thema',
                     y='Aantal vragen',
                     # color='Thema',  # You can use 'color_discrete_map' if needed
                     labels={'x': 'Thema', 'y': 'Aantal vragen'},
                     title='Vragen per thema')

    else:
        fig = px.bar()

    return fig

#Create function to load app in integrated appraoch
def register_callbacks(app):
    @app.callback(
        [Output('amount_questions', 'children'),
         Output('written_questions_graph', 'figure')],
        [Input('date-range-written-questions', 'start_date'),
         Input('date-range-written-questions', 'end_date'),
         Input('x-axis-dropdown', 'value')]
        )
    def update_display(start_date, end_date, selected_axis):
        # Filter data based on user input
        written_questions_filtered_df = filter_data(start_date, end_date, 
                                                    written_questions_df)
    	# Obtain count of relevant data, after filtering
        amount_questions = len(written_questions_filtered_df)
        
        # Create graph using user selected axis and filtered df
        written_questions_graph = update_chart(selected_axis, 
                                               written_questions_filtered_df)
    
        return [f"Deze selectie resulteert in {amount_questions} relevante vergaderingen.", # Use text formatting to allow easier build of layout
    				written_questions_graph]



# =============================================================================
# Run dash app
# =============================================================================
# # Comment out in integrated account
# if __name__ == '__main__':
#     app.run_server(debug=True)
