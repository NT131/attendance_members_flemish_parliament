# =============================================================================
# Setting up
# =============================================================================

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

minister_colors = {
    'cd&v': '#f5822a',
    'N-VA': '#ffac12',
    'Open Vld': '#003d6d',
}


# Assign groups to ministers
minister_groups = {
    'Benjamin Dalle': 'cd&v',
    'Hilde Crevits': 'cd&v',
    'Jo Broens': 'cd&v',
    'Wouter Beke': 'cd&v',
    
    'Ben Weyts': 'N-VA',
    'Jan Jambon': 'N-VA',
    'Matthias Diependaele': 'N-VA',
    'Zuhal Demir': 'N-VA',
    
    'Bart Somers': 'Open Vld',
    'Gwendolyne Rutten': 'Open Vld',
    'Lydia Peeters': 'Open Vld',
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
                # html.P("Welke parlementsleden stelden het meeste schriftelijke vragen? En welke ministers kregen de meeste schriftelijke vragen te verwerken?", className="header-description"),
                html.P("Welke parlementsleden stelden het meeste schriftelijke vragen?", className="header-description"),
                html.P("En welke ministers kregen de meeste schriftelijke vragen te verwerken?", className="header-description"),
            ],
            className="section-header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        # html.H3(
                        #     "Selecteer de relevante periode.",
                        #     className="header-subsubtitle",
                        # ),
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
                        
                        # Theme filter dropdown
                        html.Div(
                            children=[
                                html.Div(
                                    children="Selecteer thema", 
                                    className="menu-title"
                                ),
                                dcc.Dropdown(
                                    id="theme-filter",
                                    options=[
                                        {'label': 'Alle', 'value': 'Alle'}
                                        ] + [
                                        # check if theme exists to avoid empty theme option
                                        {'label': theme, 'value': theme} for theme in written_questions_df['thema'].unique() if theme
                                        ],
                                    multi=True,
                                    value='Alle',
                                    placeholder="Selecteer thema's",
                                ),
                            ],
                            className="menu-element"
                        ),
                        
                        # Minister dropdown
                        html.Div(
                            children=[
                                html.Div(
                                    children="Selecteer minister ", 
                                    className="menu-title"
                                ),
                                dcc.Dropdown(
                                    id="minister-filter",
                                    options=[
                                        {'label': 'Alle', 'value': 'Alle'},
                                        ] + [
                                        {'label': minister, 'value': minister} for minister in written_questions_df['minister'].unique()
                                    ],
                                    multi=False,
                                    value='Alle',
                                    placeholder="Selecteer minister",
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
                    className="flex-container",
                ),
            ],
            className="wrapper",
        ),
    
                                            
        dcc.Tabs([
            dcc.Tab(
                label='Algemeen',
                children=[
                    html.Div([
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
                        
                        ]),
                    ]),
            dcc.Tab(
                label='Specifieke parlementsleden',
                children=[
                    # New Div for Dropdown and DataTable
                    html.Div([
                        dcc.Dropdown(
                            id='member-dropdown',
                            # Sort options alphabetically. Important to wrap dicts in list
                            options=[
                                {'label': member, 'value': member} for member in sorted(written_questions_df['vraagsteller'].unique())
                            ],
                            multi=False,
                            value=None, # Set default value as None to avoid table being rendered automatically 
                            placeholder="Selecteer parlementslid",
                            style={'width': '50%'}
                        ),
                        html.Div(
                            id='datatable-info', 
                            style={'margin-top': '10px', 'font-size': '14px'}
                        ),

                        dash_table.DataTable(
                            id='written-questions-table',
                            columns=[
                                {'name': 'Datum vraag gesteld', 'id': 'datum gesteld'},
                                {'name': 'Bevoegde minister', 'id': 'minister'},
                                # use markdown represention to leverage clickable links of df
                                {'name': 'Onderwerp', 'id': 'onderwerp', 'presentation': 'markdown'}, 
                            ],
                            page_size=25, #  Set the number of rows per page
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
                        ),
                    ], className='custom-datatable-container'),
                ]
            ),
            # dcc.Tab(
            #     label='Antwoordtermijn',
            #     children=[
            #         html.Div([
            #             dcc.Graph(
            #                 id='question-duration-bar-plot',
            #             ),
            #         ]),
            #     ]
            # )
        ]),
    ],
    # use CSS flexbox approach to easily structure graphs and titles
    style={"display": "flex", "flex-direction": "column"} 
)



# =============================================================================
# Callback
# =============================================================================
#Define function to filter data based on user selection
def filter_data(start_date, end_date, theme_filter, 
                minister_filter, written_questions_df):   
    # Ensure correct date format
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    
    
    # Filter DataFrame with all questions further based on the date range
    written_questions_filtered_df = written_questions_df[
         (written_questions_df['datum beantwoord'] >= start_date) &
         (written_questions_df['datum beantwoord'] <= end_date)
     ]
    
    # Filter DataFrame based on the selected theme
    if theme_filter is not None and theme_filter != 'Alle':
        written_questions_filtered_df = written_questions_filtered_df[
            written_questions_filtered_df['thema'].isin(theme_filter)
        ]
    
    # Exclude entries with the same minister value
    if minister_filter is not None and minister_filter != 'Alle':
        written_questions_filtered_df = written_questions_filtered_df[
            written_questions_filtered_df['minister'] == minister_filter
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
# =============================================================================
#       # Try out various possible plots
        ## VIOLIN plot        
        # fig = px.violin(grouped_data,
        #                 # x='Parlementslid',
        #                 # y='Aantal vragen',
        #                 y='Parlementslid',
        #                 x='Aantal vragen',
        #                 color='Partij',
        #                 color_discrete_map=party_colors,
        #                 # box_width=0.2,
        #                 labels={'x': 'Parlementslid', 'y': 'Aantal vragen'},
        #                 title='Vragen per parlementslid')
        # BAR plot
        fig = px.bar(grouped_data,
                      # x='Parlementslid',
                      # y='Aantal vragen',
                      x='Aantal vragen',
                      y='Parlementslid',
                      color='Partij',
                      color_discrete_map=party_colors,
                      labels={'x': 'Parlementslid', 'y': 'Aantal vragen'},
                      title='Vragen per parlementslid')
        

        ## SCATTER plot       
        # fig = px.scatter(
        #     grouped_data,
        #     # x='Parlementslid',
        #     # y='Aantal vragen',
        #     x='Partij',
        #     y='Aantal vragen',
        #     # size=dot_sizes,
        #     # size=grouped_data['Aantal vragen'].apply(lambda x: x * 20),
        #     size='Aantal vragen',
        #     # color='blue',
        #     color='Partij',
        #     color_discrete_map=party_colors,
        #     title='Vragen per parlementslid',
        #     custom_data=["Parlementslid"],  # Include party name in custom data for hover label
        #     category_orders={"Parlementslid": grouped_data['Parlementslid'].tolist()},  # Specify the order of categories
        #     )
        
        # hover_text = (
        #     grouped_data.apply(
        #         lambda row: (
        #             f"<b>{row['Parlementslid']}</b> stelde {row['Aantal vragen']} vragen."
        #         ),
        #         axis=1,
        #     )
        # )
        
        # fig.update_traces(
        #     hovertemplate=(
        #         "%{customdata}<br><extra></extra>"
        #     ),
        #     customdata=hover_text,
        # )
# =============================================================================

        
        # # Update x-axis to reflect the sorted order
        # fig.update_xaxes(categoryorder='total descending')
        
        # Update y-axis to reflect the sorted order
        fig.update_yaxes(categoryorder='total ascending')
        
        # Modify height of entire graph (static) to ensure all entries are properly shown 
        fig.update_layout(
            height=2000,  # Set the height of the figure
            bargap=0.2,  # Set the gap between bars
            # xaxis=dict( # Show x-axis also at top of graph
            #     mirror=True,  # Show ticks and labels on both left and right
            #     showline=True,  # Show axis line
            #     showgrid=False,  # Hide grid lines
            # ),
        )
        
        
        # fig.update_traces(
        #     customdata=["Parlementslid"],  # Include party name in custom data for hover label
        #     hovertemplate="%{customdata}<br><extra></extra>",
        #     marker=dict(line=dict(width=0.5, color='black')),
        #     width=20, # Set a fixed height for each bar
        # )
        
        # # Adjust the gap between bars to achieve a similar effect to fixed bar height
        # fig.update_layout(
        #     bargap=0.2,  # Adjust the gap as needed
        #     uniformtext_minsize=0.4 * 10,  # Adjust the size factor as needed
        # )

    elif selected_axis == 'minister':
        grouped_data = written_questions_df_input['minister'].value_counts().reset_index()
        grouped_data.columns = ['Minister', 'Aantal vragen']
        grouped_data['Partij'] = grouped_data['Minister'].map(minister_groups)
        fig = px.bar(grouped_data,
                     x='Minister',
                     y='Aantal vragen',
                     color='Partij',
                     color_discrete_map=minister_colors,
                     labels={'x': 'Minister', 'y': 'Aantal vragen'},
                     title='Vragen aan ministers')
        # Update x-axis to reflect the sorted order
        fig.update_xaxes(categoryorder='total descending')
        
        # Reset height of entire graph (enlarged for 'vraagsteller)
        fig.update_layout(height=500)
        
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
        
        # Reset height of entire graph (enlarged for 'vraagsteller)
        fig.update_layout(height=500)
        
    elif selected_axis == 'thema':
        grouped_data = written_questions_df_input['thema'].value_counts().reset_index()
        grouped_data.columns = ['Thema', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Aantal vragen',
                     y='Thema',
                     # color='Thema',  # You can use 'color_discrete_map' if needed
                     labels={'x': 'Thema', 'y': 'Aantal vragen'},
                     title='Vragen per thema')
        
        # Modify height of entire graph (static) to ensure all entries are properly shown 
        fig.update_layout(
            height=600,  # Set the height of the figure
            bargap=0.2,  # Set the gap between bars
            )
        # Update y-axis to reflect the sorted order
        fig.update_yaxes(categoryorder='total ascending')
  
    else:
        fig = px.bar()

    return fig



# def answer_term_bar_chart(written_questions_df_input, num_bins=20):
#     # Ensure 'termijn antwoord (werkdagen)' is converted to numeric
#     written_questions_df_input['termijn antwoord (werkdagen)'] = pd.to_numeric(written_questions_df_input['termijn antwoord (werkdagen)'], errors='coerce')

#     # Create bins using pd.cut
#     written_questions_df_input['termijn bins'] = pd.cut(written_questions_df_input['termijn antwoord (werkdagen)'], bins=num_bins)

#     # Group by the bins and count the number of questions in each bin
#     bin_counts = written_questions_df_input.groupby('termijn bins').size().reset_index(name='Number of Questions')

#     # Create the bar chart using px.bar
#     fig = px.bar(
#         bin_counts,
#         x='termijn bins',
#         y='Number of Questions',
#         labels={'termijn bins': 'Time to Answer (Workdays)', 'Number of Questions': 'Number of Questions'},
#         title='Distribution of Time to Answer Questions',
#         color_discrete_sequence=['skyblue'],  # Bar color
#     )

#     # # Customize layout
#     # fig.update_layout(
#     #     showlegend=False,  # Hide legend for a single bar
#     # )

#     return fig



#Create function to load app in integrated appraoch
def register_callbacks(app):
    @app.callback(
        [Output('amount_questions', 'children'),
         Output('written_questions_graph', 'figure'),
         # Output('question-duration-bar-plot', 'figure'),
         Output('written-questions-table', 'data'),
         Output('datatable-info', 'children')],
        [Input('date-range-written-questions', 'start_date'),
         Input('date-range-written-questions', 'end_date'),
         Input("theme-filter", "value"),
         Input("minister-filter", "value"),
         Input('x-axis-dropdown', 'value'),
         Input('member-dropdown', 'value')]
        )
    def update_display(start_date, end_date, theme_filter, minister_filter, 
                       selected_axis, selected_member):
        # Filter data based on user input
        written_questions_filtered_df = filter_data(start_date, end_date,
                                                    theme_filter, minister_filter,
                                                    written_questions_df)
        
        # Create graph using user selected axis and filtered df
        written_questions_graph = update_chart(selected_axis, 
                                               written_questions_filtered_df)
          
        # # Create graph for answering term
        # duration_answer_graph = answer_term_bar_chart(written_questions_filtered_df)
        
        # Check if the selected axis is 'vraagsteller' to update DataTable
        if selected_axis == 'vraagsteller' and selected_member:
            # Filter data for the selected member
            selected_member_data = written_questions_filtered_df[written_questions_filtered_df['vraagsteller'] == selected_member][['datum gesteld', 'minister', 'onderwerp']]

        else:
            # If the selected axis is not 'vraagsteller', provide an empty DataFrame
            selected_member_data = pd.DataFrame()
         
        return [f"Deze selectie resulteert in {len(written_questions_filtered_df)} relevante schriftelijke vragen.", # Use text formatting to allow easier build of layout
                written_questions_graph,
                # duration_answer_graph,
                selected_member_data.to_dict('records'),
                f"Dit parlementslid stelde {len(selected_member_data)} vragen."]


# =============================================================================
# Run dash app
# =============================================================================
# # Comment out in integrated account
# if __name__ == '__main__':
#     app.run_server(debug=True)
