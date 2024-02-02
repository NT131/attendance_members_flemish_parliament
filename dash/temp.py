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


# def answer_term_bar_chart(written_questions_df_input):
#     # obtain bins and fill them with counts
#     counts, bins = np.histogram(written_questions_df_input['termijn antwoord (werkdagen)'], 
#                                       bins=range(0, int(written_questions_df_input['termijn antwoord (werkdagen)'].max()) + 5, 5))
    
#     fig = px.bar(x=bins[:-1], y=counts, labels={'x': 'Aantal werkdagen', 
#                                                  'y': 'Aantal vragen'})
#     return fig
    
# temp = answer_term_bar_chart(written_questions_df)

# temp.show()

# counts_np, bins_np = np.histogram(written_questions_df['termijn antwoord (werkdagen)'], 
#                                   bins=range(0, int(written_questions_df['termijn antwoord (werkdagen)'].max()) + 5, 5))
# counts_np
# bins_np


# Dash App
app = dash.Dash(__name__)

# grouped_data_minister = df['minister'].value_counts().reset_index()
# grouped_data_minister.columns = ['Minister', 'Aantal vragen']
# grouped_data_minister['Partij'] = grouped_data_minister['Minister'].map(minister_groups)

# # Create a DataFrame with member, count, and party columns
# grouped_data_member = df['vraagsteller'].value_counts().reset_index()
# grouped_data_member.columns = ['Parlementslid', 'Aantal vragen']
# # Apply function to create a new column 'Partij' based on fracties_dict
# grouped_data_member['Partij'] = grouped_data_member.apply(get_party, axis=1,
#                                                     facties_dict_input=fracties_dict)

# grouped_data_party = df['vraagsteller_partij'].value_counts().reset_index()
# grouped_data_party.columns = ['Partij', 'Aantal vragen']




# # Split the dataset based on the threshold value
# df_below_threshold = df[df['termijn antwoord (werkdagen)'] <= 75]
# df_above_threshold = df[df['termijn antwoord (werkdagen)'] > 75]



# df_above_threshold['Partij minister'] = df_above_threshold['minister'].map(minister_groups)

# # for the dataset with the most of the data: aggregate counts
# grouped_data_term = df_below_threshold['termijn antwoord (werkdagen)'].value_counts().reset_index()
# grouped_data_term.columns = ['termijn antwoord (werkdagen)', 'count']



# # Split the dataset based on the threshold value
# df_below_threshold = grouped_data_term[grouped_data_term['termijn antwoord (werkdagen)'] <= 75]
# df_above_threshold = grouped_data_term[grouped_data_term['termijn antwoord (werkdagen)'] > 75]


# def histogram_fig(df):
#     figure=px.histogram(df, 
#                         x='termijn antwoord (werkdagen)', 
#                         nbins=20, 
#                         labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn', 'count': 'Aantal vragen'},
#                         # title='Antwoordtermijn',
#                         )    
#     return figure
# grouped_data_term_hist = histogram_fig(grouped_data_term)

# def bar_fig_below_threshold(df):
#     figure=px.bar(df, 
#                   # x='termijn antwoord (werkdagen)', 
#                   # y='count',
#                    x='count', 
#                    y='termijn antwoord (werkdagen)',
#                   # y='vraagsteller',
#                   labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'count': 'Aantal vragen'},
#                   title='Vragen beantwoord binnen 75 werkdagen',
#                   orientation='h',
#                   # category_orders={'termijn antwoord (werkdagen)': 'descending'},  # Specify category order for y-axis
#                         )
    
#    # Update the y-axis category order
#     figure.update_yaxes(categoryorder='total ascending')
    
#     return figure

# grouped_data_term_bar_first_half = bar_fig_below_threshold(grouped_data_term)
# grouped_data_term_bar_first_half = bar_fig(df_below_threshold)


# def bar_fig_above_threshold(df):
#     figure=px.bar(df, 
#                   x='termijn antwoord (werkdagen)',
#                   y='minister',
#                   labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'mnister': 'Verantwoordelijke minister'},
#                   title='Vragen beantwoord binnen 75 werkdagen',
#                   orientation='h',
#                   color='vraagsteller_partij',
#                   color_discrete_map=party_colors,
#                   barmode='group',
#                   # category_orders={'termijn antwoord (werkdagen)': 'descending'},  # Specify category order for y-axis
#                         )
    
#     # Update the y-axis category order
#     figure.update_yaxes(categoryorder='total ascending')
    
#     return figure

# def bar_fig_above_threshold(df):
#     figure=px.scatter(df, 
#                   x='termijn antwoord (werkdagen)',
#                   y='minister',
#                   # y='vraagsteller',
#                   color='vraagsteller_partij',
#                   color_discrete_map=party_colors,
#                   labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'mnister': 'Verantwoordelijke minister'},
#                   title='Vragen beantwoord binnen 75 werkdagen',
#                   # orientation='h',
#                   # category_orders={'termijn antwoord (werkdagen)': 'descending'},  # Specify category order for y-axis
#                         )
    
#     # Update the y-axis category order
#     figure.update_yaxes(categoryorder='total ascending')

#     hover_text = (
#         df.apply(
#             lambda row: (
#                 f"<b>{row['vraagsteller']}</b> ({row['vraagsteller_partij']}) stelde op {row['datum gesteld'].strftime('%d %B %Y')} volgende schriftelijke vraag: <br>"
#                 # f"{dcc.Markdown(row['onderwerp'], dangerously_allow_html=True)}. <br>" # Use markdown to ensure clickable link
#                 # f"{html.A(row['onderwerp'], href=row['url'], target='_blank')}. <br>"
#                 f"{row['onderwerp']}. <br>"
#                 f"Minister {row['minister']} beantwoordde deze vraag na {row['termijn antwoord (werkdagen)']:.0f} werkdagen."
#             ),
#             axis=1,
#         )
#     )
    
#     figure.update_traces(
#         hovertemplate=(
#             "%{customdata}<br>"
#         ),
#         customdata=hover_text,
#     )

    
#     return figure

# def bar_fig_above_threshold(df):
#     figure = px.scatter(df, 
#                         x='termijn antwoord (werkdagen)',
#                         y='minister',
#                         color='vraagsteller_partij',
#                         color_discrete_map=party_colors,
#                         labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'mnister': 'Verantwoordelijke minister'},
#                         title='Vragen beantwoord binnen 75 werkdagen',
#                         hover_data=['vraagsteller', 'vraagsteller_partij', 'datum gesteld', 'onderwerp', 'minister', 'termijn antwoord (werkdagen)'],
#                         category_orders={'minister': 'total ascending'},
#                         )

#     figure.update_layout(hovermode='closest')

#     # Custom hover template
#     # use hover_data parameter and refer to it here instead of directly in hovertemplate text.
#     # Otherwise, this replaces layers, impacting e.g. colors. 
#     # See https://community.plotly.com/t/scatter-plot-color-and-clickdata-mismatch/66568
#     figure.update_traces(
#         hovertemplate=(
#             "<b>%{customdata[0]}</b> (%{customdata[1]}) stelde op %{customdata[2]} volgende schriftelijke vraag: <br>"
#             "%{customdata[3]}. <br>"
#             "Minister %{customdata[4]} beantwoordde deze vraag na %{customdata[5]:.0f} werkdagen."
#             "<extra></extra>"  # This is needed to ensure that all elements from hover_data are shown (vs. default of only showing subset)
#         ),
#     )

#     return figure


# def bar_fig_above_threshold(df):
#     figure = px.scatter(df, 
#                         x='termijn antwoord (werkdagen)',
#                         y='minister',
#                         color='vraagsteller_partij',
#                         color_discrete_map=party_colors,
#                         labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 
#                                 'minister': 'Verantwoordelijke minister',
#                                 'vraagsteller_partij': 'Partij parlementslid dat vraag stelde'},
#                         title='Vragen beantwoord binnen 75 werkdagen',
#                         # Use hover_data parameter and refer to it here instead of directly in hovertemplate text.
#                         # Otherwise, this replaces layers, impacting e.g. colors. 
#                         # See https://community.plotly.com/t/scatter-plot-color-and-clickdata-mismatch/66568
#                         # Only include variables in hoverlabel that are not yet used in the graph, such as in x and y
#                         hover_data=['vraagsteller', 'vraagsteller_partij', 'datum gesteld', 'onderwerp', 'url'],
#                         category_orders={'minister': 'total ascending'},
#                         )

#     # Custom hover template
#     figure.update_traces(
#         # do not use .strftime('%d %B %Y')  to format date:  Plotly doesn't directly evaluate Python expressions within the string.
#         hovertemplate=(
#             "<b>%{customdata[0]}</b> (%{customdata[1]}) stelde op %{customdata[2]} volgende schriftelijke vraag: <br>"
#             "%{customdata[3]}. <br>" 
#             # "%{dcc.Markdown(customdata[4], dangerously_allow_html=True)} <br>"
#             # f"{dcc.Markdown(row['onderwerp'], dangerously_allow_html=True)}. <br>" # Use markdown to ensure clickable link
#             "Minister %{y} beantwoordde deze vraag na %{x:.0f} werkdagen. <br>"
#             "<extra></extra>" # This is needed to ensure that all elements from hover_data are shown (vs. default of only showing subset)
#         ),
#     )

#     return figure


# bar_second_half = bar_fig_above_threshold(df_above_threshold)

# def scatter_fig(df):
#     figure = px.scatter(df_above_threshold, 
#                       x='termijn antwoord (werkdagen)', 
#                       y='vraagsteller_partij', 
#                       color='Partij minister',
#                       color_discrete_map=minister_colors,
#                       title='Scatter Plot (> 75)')
    
#     return figure


# def scatter_fig(df_input):
#     fig = px.scatter(
#         df_input, 
#         x='termijn antwoord (werkdagen)', 
#         y='minister', 
#         color='vraagsteller_partij',
#         color_discrete_map=party_colors,
#         # color_discrete_map=minister_colors,
#         # size=20,
#         labels={'termijn antwoord (werkdagen)': 'Antwoordtermijn (werkdagen)', 'minister': 'Verantwoordelijke minister'},
#         title='Vragen beantwoord na 75 werkdagen')

#     hover_text = (
#         df_input.apply(
#             lambda row: (
#                 f"<b>{row['vraagsteller']}</b> ({row['vraagsteller_partij']}) stelde op {row['datum gesteld'].strftime('%d %B %Y')} volgende schriftelijke vraag: <br>"
#                 # f"{dcc.Markdown(row['onderwerp'], dangerously_allow_html=True)}. <br>" # Use markdown to ensure clickable link
#                 # f"{html.A(row['onderwerp'], href=row['url'], target='_blank')}. <br>"
#                 f"{row['onderwerp']}. <br>"
#                 f"Minister {row['minister']} beantwoordde deze vraag na {row['termijn antwoord (werkdagen)']:.0f} werkdagen."
#             ),
#             axis=1,
#         )
#     )
    
#     fig.update_traces(
#         hovertemplate=(
#             "%{customdata}<br>"
#         ),
#         customdata=hover_text,
#     )


#     return fig

# df_above_threshold_fig = scatter_fig(df_above_threshold)


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
        figure=graph_below_threshold,
    ),
    
    dcc.Graph(
        id='scatter-plot',
        figure=graph_above_threshold,
    )
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

    return figure



@app.callback(
        [Output('bar-plot', 'figure'), 
        Output('scatter-plot', 'figure')],
        [Input('threshold', 'int')])

def update_reply_term_graphs(threshold):
    
    (df_below_threshold_grouped_filtered, 
     df_above_threshold_filtered) = split_data_on_threshold(
         written_questions_df, 
         threshold)
    
    graph_below_threshold = bar_fig_below_threshold(
        df_below_threshold_grouped_filtered,
        threshold)
    
    graph_above_threshold = scatter_fig_above_threshold(
        df_above_threshold_filtered,
        threshold)
    
    return graph_below_threshold, graph_above_threshold



# grouped_data_term_bar_first_half = bar_fig_below_threshold(grouped_data_term, threshold)



@app.callback(
        Output('scatter-plot', 'figure'), 
        [Input('scatter-plot', 'clickData')])


# Make Datapoints of scatterplot clickable, returning webpage of question
# see https://stackoverflow.com/questions/25148462/open-a-url-by-clicking-a-data-point-in-plotly
def open_url(clickData):
    if clickData != None:
        # Obtain url as stored in customdata
        url = clickData['points'][0]['customdata'][4]
        # Navigate to url in new tab of webbrowser
        webbrowser.open_new_tab(url)
    else:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)

# df['termijn antwoord (werkdagen)'].min()
# df['termijn antwoord (werkdagen)'].max()
