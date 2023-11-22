# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
#Data manipulation
import pandas as pd

#Visualizing
import plotly.express as px

#Importing dash
import dash
from dash import html, dcc, Input, Output, dash_table, ctx, callback
import dash_bootstrap_components as dbc


'''PART1: Reading Input datafiles'''
input_path = os.path.dirname(__file__) + "\\Processed Data\\"
grouped_df = pd.read_csv(input_path + 'grouped_df.csv')
top_df = pd.read_csv(input_path + 'top_df.csv')
non_norm_grouped = pd.read_csv(input_path + 'non_norm_df.csv')
cleaned_df = pd.read_csv(input_path + 'cleaned_df.csv')

#Defining input data structurs
all_sites = grouped_df['VIRTUAL_LINE'].drop_duplicates().tolist()
all_modules = grouped_df['MODULE'].drop_duplicates().tolist()
all_lineview_vars = grouped_df.drop(columns = ['MODULE', 'VIRTUAL_LINE']).columns.tolist()

'''PART2: Defining app structure and callbacks'''
# initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
pd.options.display.float_format = '${:.2f}'.format
colors = {'background': '#A5D8DD',
        'text': '#7FDBFF'}

# set app layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, 
                      children = [
    html.Div(children = [
        html.H1('Module Comparison', style={'textAlign':'LEFT','backgroundColor': '#4CB5F5', 'borderRadius': '5px'}),
        html.Div(children='A high dimensional module - module and entity - entity comparison for outlier detection.'),
        html.Br(),
        html.Div(children = [
            html.Label('Site'),
            dcc.Dropdown(options =  [{"label": i, "value": i} for i in grouped_df['VIRTUAL_LINE'].drop_duplicates()] + 
                             [{'label': 'Select all', 'value': 'all_values'}],
                             value = 'all_values',
                             id='site--filter'),
            html.Label('Module'),
            dcc.Dropdown(options =  [{"label": i, "value": i} for i in grouped_df['MODULE'].drop_duplicates()] + 
                             [{'label': 'Select all', 'value': 'all_values'}],
                             value = 'all_values',
                             id='module--filter'),
            html.Label('Lineview Variable'),
            dcc.Dropdown(options =  [{"label": i, "value": i} for i in all_lineview_vars] + 
                             [{'label': 'Select all', 'value': 'all_values'}],
                             value = 'all_values',
                             multi = True,
                             id='lineview--filter')


        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div(children = [
                html.Button('MAE', id='btn-nclicks-1', n_clicks=0),
                html.Button('LOF', id='btn-nclicks-2', n_clicks=0),
                html.Button('IsolationForest', id='btn-nclicks-3', n_clicks=0),
            
            dbc.Button('🡠', id='back-button', outline=True, size="sm",
                        className='mt-2 ml-2 col-1', style={'display': 'none'}),
            dcc.Graph(id = 'module_clustering',
                                    figure = {})],
                                    style={'width': '49%', 'display': 'inline-block'})
        
    ]),
    html.Br(),                   
    html.Div(children = [
        html.Div(children = [
                dcc.Graph(id = 'module_compare',
                                figure = {})], 
                                style={'width': '49%', 'display': 'inline-block'}),
    
        html.Div(children = [ 
                dash_table.DataTable(id = 'module_table',
                                 columns = [{"name": i, "id": i} for i in non_norm_grouped.columns],
                                 data = non_norm_grouped.head(10).to_dict('records'),
                                 page_size = 10,
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
                                style_table={
                                    'overflowX': 'auto'
                                })
        ],style={'width': '49%', 'display': 'inline-block'})
    ], className = 'row')
])
      

'''PART 2: Defining Callbacks'''
# Updating module compare and table
@app.callback(Output(component_id = 'module_compare', component_property = 'figure'),
              [Input('site--filter', 'value'),
              Input('module--filter', 'value')])

    
def update_grouped_df(site, module):
    
    #If all values is chosen select all recipes
    site_list = []
    module_list = []
        
    #Filtering for site
    if site == 'all_values':
        site_list = grouped_df['VIRTUAL_LINE'].unique().tolist()
    else:
        site_list = [site]
    #Filtering for module
    if module == 'all_values':
        module_list = grouped_df['MODULE'].unique().tolist()
    else:
        module_list = [module]
            
    df = grouped_df[(grouped_df['MODULE'].isin(module_list)) &
                            (grouped_df['VIRTUAL_LINE'].isin(site_list))]
    
    
    #Filtering Dataframe: Defaults to top module unless user selects something else
    filtered_df = ""
    if site == 'all_values' and module == 'all_values':
        filtered_df = df[df['MODULE'].isin(top_df['MODULE'])]
    elif module == 'all_values':
        filtered_df = df[(df['MODULE'].isin(top_df['MODULE'])) &
                        (df['VIRTUAL_LINE'].isin(site_list))]
    elif site == 'all_values':
        filtered_df = df[df['MODULE'].isin(module_list)]
    else:
        filtered_df = df[(df['MODULE'].isin(module_list)) &
                        (df['VIRTUAL_LINE'].isin(site_list))]
        
    print(filtered_df.columns)
    #Pivoting data long
    var_list = list(top_df.drop(columns = ['MODULE', 'VIRTUAL_LINE', 'Module_Score', 'MAE']).columns)
    long_top_df =  pd.melt(filtered_df, id_vars = ['MODULE', 'VIRTUAL_LINE'],
                           value_vars=var_list,value_name='Variable Score', 
                           ignore_index=False)
    #Graphing data
    module_compare_figure = px.bar(long_top_df, x="VIRTUAL_LINE", y="Variable Score", color="variable",
                             facet_col="MODULE",facet_col_wrap = 5,
                             title="Outlier Module Comparison by Site")


    return module_compare_figure



# Updating module compare and table
@app.callback([Output(component_id = 'module_clustering', component_property = 'figure'),
               Output('back-button', 'style'),
               Output(component_id = 'module_table', component_property = 'data')],
              [Input('site--filter', 'value'),
               Input('module--filter', 'value'),
               Input('module_clustering', 'clickData'),    #for getting the vendor name from graph
               Input('back-button', 'n_clicks'),#Backbutton for returning
               Input('btn-nclicks-1', 'n_clicks'),
               Input('btn-nclicks-2', 'n_clicks'),
               Input('btn-nclicks-3', 'n_clicks')]) 

    
def drilldown(site, module,click_data,n_clicks, click1, click2, click3):
    
    #Checking which input was fired
    ctx = dash.callback_context

    #Choosing anomaly metric based on input buttons
    distance_measure = 'MAE'
    if "btn-nclicks-2" == ctx.triggered_id:
        distance_measure = 'LOF'
    elif "btn-nclicks-3" == ctx.triggered_id:
        distance_measure = 'IsolationForest'
    
    #If all values is chosen select all recipes
    site_list = []
    module_list = []
    #Filtering for site
    if site == 'all_values':
        site_list = grouped_df['VIRTUAL_LINE'].unique().tolist()
    else:
        site_list = [site]
    #Filtering for module
    if module == 'all_values':
        module_list = grouped_df['MODULE'].unique().tolist()
    else:
        module_list = [module]
        
    #Filtering graph dataframe for all figures    
    df = grouped_df[(grouped_df['MODULE'].isin(module_list)) &
                            (grouped_df['VIRTUAL_LINE'].isin(site_list))]
    #Filtering non-normalized dataframe for table display
    df_table = non_norm_grouped[(non_norm_grouped['MODULE'].isin(module_list)) &
                               (non_norm_grouped['VIRTUAL_LINE'].isin(site_list))]
    
    #Checking which input was fired for graph drilldown
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    #If graph has been triggered
    if trigger_id == 'module_clustering':

        # get vendor name from clickData
        if click_data is not None:
            module = click_data['points'][0]['x']
            #Updating graph
            entity_df = cleaned_df[cleaned_df['MODULE'] == module]
            entity_fig = px.bar(entity_df, x='PARENT', y='Avg(CT)')
            
            #Updating datatable
            df_table = df_table[df_table['MODULE'] == module]

            return entity_fig, {'display':'block'}, df_table.to_dict("records")
    
    #If graph hasnt been triggered returning factory level graph
    else:
            
        #Updating module clustering
        global_average = 0
        var = df[distance_measure].std()
        
        #Module clustering graph
        module_clustering_fig = px.scatter(df, x = 'MODULE', y = distance_measure, color = 'VIRTUAL_LINE', 
                         title = 'Module Performance Comparison')
        module_clustering_fig.add_hline(y=global_average - 2*var, line_dash="dash",
                     annotation_text="-2 Sigma LCL")
        module_clustering_fig.add_hline(y=global_average + 2*var, line_dash="dash",
                     annotation_text="+2 Sigma UCL")


        return module_clustering_fig, {'display':'none'}, df_table.to_dict("records")
    
'''PART3: Running App'''
if __name__ == "__main__":
    app.run_server(debug=False)
