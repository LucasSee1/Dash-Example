# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 17:21:11 2023

@author: lsee
"""
import pandas as pd
from pathlib import Path
import pyodbc
from scipy import stats
import PyUber
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

'''PART 2: Displaying in App'''

#Initializing data structures

# initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

colors = {
        'background': '#A5D8DD',
        'text': '#7FDBFF'}

    
# set app layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children = [
    html.H1('Runrate Dashboard', style={'textAlign':'center','backgroundColor': '#4CB5F5', 'borderRadius': '5px'}),
    html.Br(),
    html.Div(children = [
        html.Div(children = [ 
            html.Div(children = [ 
                
                html.Label('Recipe Filter'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in recipes] + [{'label': 'Select all', 'value': 'all_values'}],
                         value = 'all_values',
                         multi=True,
                         id='recipe--filter'),
                html.Label('Recipe In MOR'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in mor_options],
                         value = mor_options[0],
                         multi=True,
                         id='MOR--filter'),
                html.Label('Top X Recipes By Outs'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in range(1,len(recipes)+1)],
                         value = len(recipes),
                         multi=False,
                         id='top_x--filter'),
                html.Label('Lot Classification'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in lot_classification],
                         value = ['1st Lot', 'Nth Lot'],
                         multi=True,
                         id='lot_classification--filter')
            ],style={'width': '49%', 'display': 'inline-block'}),
            
            html.Div(children = [   
                html.Label('Chem Cascade'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in chem_cascade],
                         value = chem_cascade,
                         multi=True,
                         id='chem_cascade--filter'),
                 html.Label('Runrate'),
                 dcc.Slider(
                    df['individual_lot_rr'].min(),
                    df['individual_lot_rr'].max(),
                    step=None,
                    id='crossfilter-runrate--slider',
                    value=df['individual_lot_rr'].max(),
                    marks={str('individual_lot_rr'): str('individual_lot_rr') for individual_lot_rr in df['individual_lot_rr'].unique()}),

                html.Label('processed_wafer_count'),
                dcc.Dropdown(options =  [{"label": i, "value": i} for i in wafer_counts],
                         value = [max(wafer_counts)],
                         multi=True,
                         id='crossfilter-wafer--slider'),
                 html.Label('chamber_counts'),
                 html.Br(),
                  dcc.Dropdown(options =  [{"label": i, "value": i} for i in chamber_counts],
                         value = [max(chamber_counts)],
                         multi=True,
                         id='crossfilter-chamber--slider')
            ],style={'width': '49%', 'display': 'inline-block'})
           
            
            
        ],style={'padding': 10, 'flex': 1}),
        html.Div(children = [ 
            dash_table.DataTable(id = 'table',
                                 columns = [{"name": i, "id": i} for i in rr_df.columns],
                                data = [],
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Date', 'Region']
                                ],
                                style_data={
                                    'color': 'black',
                                    'backgroundColor': 'white'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(220, 220, 220)',
                                    }
                                ],
                                style_header={
                                    'backgroundColor': 'rgb(210, 210, 210)',
                                    'color': 'black',
                                    'fontWeight': 'bold'
                                })
        ],style={'width': '49%', 'display': 'inline-block'})
    ], className="row"),
    html.Div(children = [html.H1('Visualizations', style={'textAlign':'center', 'backgroundColor': '#4CB5F5', 'borderRadius': '5px'})],
          className = "row"),   
    html.Div([
            html.Div([
                dcc.Graph(id='histogram', figure = {})],style={'width': '49%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='rr_by_cascade_group', figure = {})],style={'width': '49%', 'display': 'inline-block'})],
         className = "row"),

    html.Div([
        html.Div([
                dcc.Graph(id = 'correlation',
                      figure = px.bar(corr_matrix, x='variable', y='individual_lot_rr'))], 
                      style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
                dcc.Graph(id = 'feature_importance',
                      figure = px.bar(feature_df, x='feature', y='importance'))], 
                      style={'width': '49%', 'display': 'inline-block'})],
        className = "row")
        
]
)