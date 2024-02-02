#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 15:02:44 2024

@author: niels_tack
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
# import numpy as np

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import pickle

import webbrowser
from dash.exceptions import PreventUpdate

from attendance_statistics import get_party

# Load df with written questions and information about parties
written_questions_df = pd.read_pickle('../data/details_questions_term_df.pkl')

party_colors = {'Groen': '#83de62',
    'Onafhankelijke': '#787878',
    'Vooruit': '#FF2900',
    'Vlaams Belang': '#ffe500',
    'cd&v': '#f5822a',
    'N-VA': '#ffac12',
    'Open Vld': '#003d6d',
    'PVDA': '#AA050E'
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

minister_colors = {
    'cd&v': '#f5822a',
    'N-VA': '#ffac12',
    'Open Vld': '#003d6d',
}

# Load information about parties
with open('../data/fracties.pkl', 'rb') as file:
    fracties_dict = pickle.load(file)



# Dash App
app = dash.Dash(__name__)




app.layout = html.Div([
    # dcc.Graph(
    #     id='scatter-plot',
    #     figure=px.scatter(df, 
    #                       x='datum gesteld', 
    #                       y='termijn antwoord (werkdagen)', 
    #                       labels={'termijn antwoord (werkdagen)': 'Duration of Answer (days)'},
    #                       title='Scatter Plot of Duration of Answers')
    # ),
    
   html.Div([
       html.Label("Drempelwaarde antwoordtermijn (aantal werkdagen)"),
       dcc.Input(
           id='threshold', 
           type='number', 
           value=75, # Default value
           style={'width': '50%'}
       ),
   ]),

    dcc.Graph(
        id='bar-plot',
        # figure=graph_below_threshold,
    ),
    
    dcc.Graph(
        id='scatter-plot',
        # figure=graph_above_threshold,
    ),
    # Hidden div as placeholder for output callback of clickable datapoints
    html.Div(id='hidden-div', style={'display': 'none'})  

])

# Function to split data based on the provided threshold
def split_data_on_threshold(df, threshold: int):
    # Split the dataset based on the threshold value
    df_below_threshold = df[df['termijn antwoord (werkdagen)'] <= threshold]
    df_above_threshold = df[df['termijn antwoord (werkdagen)'] > threshold]

    # Add new column to indicate party of the relevant minister
    df_above_threshold['Partij minister'] = df_above_threshold['minister'].map(minister_groups)

    # for the dataset with the data below the threshold: aggregate counts
    df_below_threshold_grouped = df_below_threshold['termijn antwoord (werkdagen)'].value_counts().reset_index()
    df_below_threshold_grouped.columns = ['termijn antwoord (werkdagen)', 'count']
    
    return df_below_threshold_grouped, df_above_threshold

# Function to get bar plot for dataset below threshold
def bar_fig_below_threshold(df, threshold):
    figure=px.bar(df,
                  x='count', 
                  y='termijn antwoord (werkdagen)',
                  labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'count': 'Aantal vragen'},
                  title=f"Vragen beantwoord binnen {threshold} werkdagen",
                  orientation='h',
                  )
    
   # Update the y-axis category order
    figure.update_yaxes(categoryorder='total ascending')
    
    # Add red horizontal line at position 20
    figure.add_shape(
        go.layout.Shape(
            type="line",
            x0=0, # start line at 0
            x1=df['count'].max() * 1.1, # continue line up until highest amount of questions + 20% further
            y0=20,
            y1=20,
            line=dict(color="red", width=1),
        ),
    )
    
    # Add label for the line
    figure.add_annotation(
        go.layout.Annotation(
            x=df['count'].max() / 2,
            y=25,
            xref="x",  
            yref="y",
            text="Reglementaire antwoordtermijn: 20 werkdagen",
            showarrow=False,
        ),
    )
    
    return figure

# Function to get scatter plot for dataset above threshold
def scatter_fig_above_threshold(df, threshold):
    figure = px.scatter(df, 
                        x='termijn antwoord (werkdagen)',
                        y='minister',
                        color='vraagsteller_partij',
                        color_discrete_map=party_colors,
                        labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 
                                'minister': 'Verantwoordelijke minister',
                                'vraagsteller_partij': 'Partij parlementslid dat vraag stelde'},
                        title=f"Vragen beantwoord binnen {threshold} werkdagen",
                        # Use hover_data parameter and refer to it here instead of directly in hovertemplate text.
                        # Otherwise, this replaces layers, impacting e.g. colors. 
                        # See https://community.plotly.com/t/scatter-plot-color-and-clickdata-mismatch/66568
                        # Only include variables in hoverlabel that are not yet used in the graph, such as in x and y
                        hover_data=['vraagsteller', 'vraagsteller_partij', 'datum gesteld', 'onderwerp', 'url'],
                        category_orders={'minister': 'total ascending'},
                        )

    # Custom hover template
    figure.update_traces(
        # do not use .strftime('%d %B %Y')  to format date:  Plotly doesn't directly evaluate Python expressions within the string.
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]}) stelde op %{customdata[2]} volgende schriftelijke vraag: <br>"
            "%{customdata[3]}. <br>" 
            "Minister %{y} beantwoordde deze vraag na %{x:.0f} werkdagen. <br>"
            "<extra></extra>" # This is needed to ensure that all elements from hover_data are shown (vs. default of only showing subset)
        ),
    )
    
    # Add footnote to indicate clickable nature of data points
    figure.update_layout(annotations=[
        dict(
            x=0, # left side
            y=-0.15,
            showarrow=False,
            text="Klik op datapunt voor meer informatie",
            xref="paper",
            yref="paper",
            font=dict(size=12, color="gray"),
        )
    ])

    return figure


@app.callback(
    Output('hidden-div', 'children'),  # Use a hidden div as a dummy output
    [Input('scatter-plot', 'clickData')]
)
# Make Datapoints of scatterplot clickable, returning webpage of question
# see https://stackoverflow.com/questions/25148462/open-a-url-by-clicking-a-data-point-in-plotly
def open_url(clickData):
    if clickData is not None:
        url = clickData['points'][0]['customdata'][4]
        webbrowser.open_new_tab(url)
    else:
        raise PreventUpdate

@app.callback(
    [Output('bar-plot', 'figure'), 
    Output('scatter-plot', 'figure')],
    [Input('threshold', 'value')])

def update_graph(threshold):
    df_below_threshold_grouped_filtered, df_above_threshold_filtered = split_data_on_threshold(
        written_questions_df, threshold
    )

    graph_below_threshold = bar_fig_below_threshold(
        df_below_threshold_grouped_filtered, threshold
    )

    graph_above_threshold = scatter_fig_above_threshold(
        df_above_threshold_filtered, threshold
    )

    return graph_below_threshold, graph_above_threshold



if __name__ == '__main__':
    app.run_server(debug=True)








