#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:13:24 2024

@author: niels_tack
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# import plotly.graph_objs as go
# from plotly.subplots import make_subplots


import pandas as pd
import plotly.express as px


# from datetime import datetime
# import locale

import pickle

# Load df with written questions and information about parties
written_questions_df = pd.read_pickle('../data/details_questions_term_df.pkl')
# Load information about parties
with open('../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)

# with open('../data/parlementsleden.pkl', 'rb') as file:
#     parlementsleden_all_dict = pickle.load(file)
 
    
def find_key(dictionary, search_value):
    for key, values in dictionary.items():
        for value in values:
            if search_value in value:
                return key
    return None  # Return None if the value is not found in any list

# # Function to get party color based on the provided dictionary
# def get_party_color(row):
#     # Obtain member's name
#     parliamentarian_name = row['Parlementslid']
#     # Obtain party of member
#     party_of_member = find_key(dictionary = fracties_dict,
#                                search_value = parliamentarian_name)
#     # if this yields no error: obtain relevant color
#     if party_of_member:
#         color_of_party = party_colors[party_of_member]
#         return color_of_party
#     else:
#         return None
    
# Function to get party color based on the provided dictionary
def get_party(row):
    # Obtain member's name
    parliamentarian_name = row['Parlementslid']
    # Obtain party of member
    party_of_member = find_key(dictionary = fracties_dict,
                               search_value = parliamentarian_name)
    # if this yields no error: obtain relevant color
    if party_of_member:
        return party_of_member
    else:
        return None


# # Function to map member to party
# def map_member_to_party(member):
#     for key, value in parlementsleden_all_dict.items():
#         if value[0] == member:
#             return value[1]
#     return None  # Handle the case where member is not found

# # Aggregate questions per party
# written_questions_df['vraagsteller_partij'] = written_questions_df['vraagsteller'].map(map_member_to_party)

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

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Schriftelijke vragen"),
    dcc.Dropdown(
        id='x-axis-dropdown',
        options=[
            {'label': 'Vraagsteller', 'value': 'vraagsteller'},
            {'label': 'Partij', 'value': 'partij'},
            {'label': 'Minister', 'value': 'minister'},
        ],
        value='vraagsteller', # Default value
        style={'width': '50%'}
    ),
    dcc.Graph(id='bar-chart')
])


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('x-axis-dropdown', 'value')]
)
def update_chart(selected_axis):
    if selected_axis == 'vraagsteller':
        # fig = px.bar(written_questions_df['vraagsteller'].value_counts(), 
        #               x=written_questions_df['vraagsteller'].value_counts().index, 
        #               y=written_questions_df['vraagsteller'].value_counts().values,
        #               color=written_questions_df['vraagsteller_partij'],
        #               color_discrete_map=party_colors,
        #               labels={'x': 'Parlementslid', 'y': 'Aantal vragen'}, 
        #               title='Vragen per parlementsleden')
        
        # Create a DataFrame with member, count, and party columns
        grouped_data = written_questions_df['vraagsteller'].value_counts().reset_index()
        grouped_data.columns = ['Parlementslid', 'Aantal vragen']
        
        # # Apply function to create a new column 'Partij kleur' based on 
        # grouped_data['Partij kleur'] = grouped_data.apply(get_party_color, axis=1)
        # Apply function to create a new column 'Partij' based on 
        grouped_data['Partij'] = grouped_data.apply(get_party, axis=1)
        
        # # Sort the DataFrame by 'Aantal vragen'
        # grouped_data = grouped_data.sort_values(by='Aantal vragen', ascending=False)

        fig = px.bar(grouped_data,
                     x='Parlementslid',
                     y='Aantal vragen',
                     color='Partij',
                     color_discrete_map=party_colors,
                     labels={'x': 'Parlementslid', 'y': 'Aantal vragen'},
                     title='Vragen per parlementslid')
        
        # Update x-axis to reflect the sorted order
        fig.update_xaxes(categoryorder='total descending')
        
        # # Assuming you have the column 'vraagsteller' in written_questions_df
        # fig = px.bar(written_questions_df['vraagsteller'].value_counts(), 
        #              x=written_questions_df['vraagsteller'].value_counts().index, 
        #              y=written_questions_df['vraagsteller'].value_counts().values,
        #              color=written_questions_df['vraagsteller_partij'],
        #              color_discrete_map=party_colors,
        #              labels={'x': 'Parlementslid', 'y': 'Aantal vragen'}, 
        #              title='Vragen per parlementsleden')
    elif selected_axis == 'minister':
        grouped_data = written_questions_df['minister'].value_counts().reset_index()
        grouped_data.columns = ['Minister', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Minister',
                     y='Aantal vragen',
                     color='Minister',
                     color_discrete_map=minister_colors,
                     labels={'x': 'Minister', 'y': 'Aantal vragen'},
                     title='Vragen aan ministers')
        # fig = px.bar(written_questions_df['minister'].value_counts(), 
        #              x=written_questions_df['minister'].value_counts().index, 
        #              y=written_questions_df['minister'].value_counts().values, 
        #              labels={'x': 'Minister', 'y': 'Aantal vragen'}, 
        #              title='Vragen aan ministers')
    elif selected_axis == 'partij':
        # grouped_data = written_questions_df.groupby('vraagsteller_partij').size().reset_index(name='question_count')
        # fig = px.bar(grouped_data, x='vraagsteller_party', y='question_count', title='Vragen per partij')
        # fig = px.bar(written_questions_df['vraagsteller_partij'].value_counts(), 
        #              x=written_questions_df['vraagsteller_partij'].value_counts().index, 
        #              y=written_questions_df['vraagsteller_partij'].value_counts().values, 
        #              color='vraagsteller_partij',
        #              color_discrete_map=party_colors,
        #              labels={'x': 'Partij', 'y': 'Aantal vragen'}, 
        #              title='Vragen gesteld per partij')
        grouped_data = written_questions_df['vraagsteller_partij'].value_counts().reset_index()
        grouped_data.columns = ['Partij', 'Aantal vragen']
        fig = px.bar(grouped_data,
                     x='Partij',
                     y='Aantal vragen',
                     color='Partij',
                     color_discrete_map=party_colors,
                     labels={'x': 'Partij', 'y': 'Aantal vragen'},
                     title='Vragen gesteld per partij')

    else:
        fig = px.bar()

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
