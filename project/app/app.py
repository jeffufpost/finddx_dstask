from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate
import pandas as pd
import dash
import plotly.express as px
import numpy as np

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

MAX_COUNTRIES = 6

# Below function to set all columns as numeric except for the index
def listofdicts(list_dicts, newdict):
    list_dicts.append(newdict)
    return list_dicts

# Download the data and set it up
df = pd.read_csv("https://raw.githubusercontent.com/finddx/FINDCov19TrackerData/master/processed/data_all.csv")
df.time = pd.to_datetime(df.time)
df = df[df.set == 'country']
df = df.sort_values(['name','time'])
df = df.set_index(['name','time'])

# Wrangle data for question 1
# Purposely removed 'cum_tests_orig' as it seems to be calculated from 'new_tests_orig' and is not a separate information
df1 = df[['new_tests_orig', 'new_cases_orig', 'new_deaths_orig']]
df1 = df1.rename(columns = {'new_tests_orig':'# of days reporting tests', 'new_cases_orig':'# of days reporting cases', 'new_deaths_orig':'# of days reporting deaths'})
# Replace zeros with NaN as described in question - keep in mind very early on in the pandemic, the 0 may actually be a report
df1 = df1.replace(to_replace=0, value=np.nan, inplace=False)
# Count the number of non NaN values per month/quarter
dfna = df1.isna()   # This will set to true all NaN values (which now includes all 0s)
dfna = ~dfna        # This will invert it, setting all non NaN values to True, which is what we want to count
df1q = dfna.groupby(['name', pd.Grouper(freq='Q', level=1)]).sum().reset_index() #Resample Quarterly
df1m = dfna.groupby(['name', pd.Grouper(freq='M', level=1)]).sum().reset_index() #Resample Monthly

# Wrangle data for question 2
df2 = df[['cap_new_tests', 'cap_new_cases', 'cap_new_deaths']]
df2= df2.rename(columns = {'cap_new_tests':'Mean test rate per 1000 people', 'cap_new_cases':'Mean case rate per 1000 people', 'cap_new_deaths':'Mean death rate per 1000 people'})
# Here instead we replace NaN with 0s
df2 = df2.replace(to_replace=np.nan, value=0, inplace=False)
df2q = df2.groupby(['name', pd.Grouper(freq='Q', level=1)]).mean().reset_index()  #Resample Quarterly
df2m = df2.groupby(['name', pd.Grouper(freq='M', level=1)]).mean().reset_index()  #Resample Monthly

# Wrangle data for question 4
# First quarterly data
df4q = df1q.copy()
df4q[['Mean test rate per 1000 people', 'Mean case rate per 1000 people', 'Mean death rate per 1000 people']] = df2q[['Mean test rate per 1000 people', 'Mean case rate per 1000 people', 'Mean death rate per 1000 people']]
# Now monthly data
df4m = df1m.copy()
df4m[['Mean test rate per 1000 people', 'Mean case rate per 1000 people', 'Mean death rate per 1000 people']] = df2m[['Mean test rate per 1000 people', 'Mean case rate per 1000 people', 'Mean death rate per 1000 people']]

### Done with data

tabs_styles = {
    'height': '44px',
    'align-items':'center',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.H3('Jeffrey Post - FINDDX Data Science Task', style = {'margin-bottom': '0px', 'color': 'black'}),
                ])
            ], className = "create_container1 five columns", id = "title"),
        ], id = "header", className = "row flex-display", style = {'text-alin': 'center', "margin-bottom": "25px"}),

    html.Div([
        html.Div([
            dcc.Tabs(id="tabs-styled-with-inline", value='question1', children=[
                dcc.Tab(label='Question 1', value='question1', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Question 2', value='question2', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Question 4', value='question4', style=tab_style, selected_style=tab_selected_style),
            ], style=tabs_styles),
            html.Div(id='tabs-content-inline')
        ], className = "create_container3 eight columns", ),
    ], className = "row flex-display"),
])

def question1_content():
    return html.Div([
        
        html.Div([
            html.P('Calculate the number of days that each country reported tests, cases and deaths per month or per quarter.', style= {'border':'3px', 'border-style':'solid', 'border-color':'#FF0000', 'padding':'1em'}),
        ]),

        html.Div([
            html.Div([
                html.P('Select up to 6 countries', className = 'fix_label', style = {'color': 'black', 'margin-top': '2px'}),
                dcc.Dropdown(
                    df.reset_index().name.unique(),
                    ['Switzerland'],
                    multi=True,
                    id='dropdown_country',
                    className = 'dcc_compon'
                ),
            ], className = "create_container3 ten columns", style = {'margin-bottom': '20px'}),
        ], className = "row flex-display"),

        html.P(id='err1', style={'color': 'red'}),

        html.Div([
            dcc.Dropdown(
                ['# of days reporting tests','# of days reporting cases','# of days reporting deaths'],
                '# of days reporting tests',
                id='dropdown_metric1',
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
# Below is code to have a dropdown menu instead of radoi items
#            dcc.Dropdown(
#                ['Monthly', 'Quarterly'],
#                'Monthly',
#                id='dropdown_resample',
#                clearable=False
#            ),
            dcc.RadioItems(
                ['Monthly', 'Quarterly'], 'Monthly',
                id='dropdown_resample',
                inline=True,
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        dash_table.DataTable(
            id='tbl1',
            data=[],
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'textAlign':'center',
            },
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    "if": {"column_id": 'time'},
                    "fontWeight": "bold",
                    #'textAlign':'right',
                },
            ],
        ),
    ])

def question2_content():
    return html.Div([

        html.Div([
            html.P('Calculate the monthly and quarterly average testing, case and death rate per capita (per 1000 people) per country.', style= {'border':'3px', 'border-style':'solid', 'border-color':'#FF0000', 'padding':'1em'}),
        ]),

        html.Div([
            html.Div([
                html.P('Select up to 6 countries', className = 'fix_label', style = {'color': 'black', 'margin-top': '2px'}),
                dcc.Dropdown(
                    df.reset_index().name.unique(),
                    ['Switzerland'],
                    multi=True,
                    id='dropdown_country',
                    className = 'dcc_compon'
                ),
            ], className = "create_container3 ten columns", style = {'margin-bottom': '20px'}),
        ], className = "row flex-display"),

        html.P(id='err2', style={'color': 'red'}),

        html.Div([
            dcc.Dropdown(
                ['Mean test rate per 1000 people', 'Mean case rate per 1000 people', 'Mean death rate per 1000 people'],
                'Mean test rate per 1000 people',
                id='dropdown_metric2',
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                ['Monthly', 'Quarterly'], 'Monthly',
                id='dropdown_resample',
                inline=True,
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        dash_table.DataTable(
            id='tbl2',
            data=[],
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'textAlign':'center',
            },
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    "if": {"column_id": 'time'},
                    "fontWeight": "bold",
                    #'textAlign':'right',
                },
            ],
        ),
    ])

def question4_content():
    return html.Div([

        html.Div([
            html.P('Create interactive boxplots to show a country on the x axis and any one of the monthly or quarterly metrics calculated in questions 1 and 2.', style= {'border':'3px', 'border-style':'solid', 'border-color':'#FF0000', 'padding':'1em'}),
        ]),

        html.Div([
            html.Div([
                html.P('Select up to 6 countries', className = 'fix_label', style = {'color': 'black', 'margin-top': '2px'}),
                dcc.Dropdown(
                    df.reset_index().name.unique(),
                    ['Switzerland'],
                    multi=True,
                    id='dropdown_country',
                    className = 'dcc_compon'
                ),
            ], className = "create_container3 ten columns", style = {'margin-bottom': '20px'}),
        ], className = "row flex-display"),

        html.P(id='err4', style={'color': 'red'}),

        html.Div([
            dcc.Dropdown(
                ['# of days reporting tests','# of days reporting cases','# of days reporting deaths','Mean test rate per 1000 people','Mean case rate per 1000 people','Mean death rate per 1000 people'],
                '# of days reporting tests',
                id='dropdown_metric4',
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                ['Monthly', 'Quarterly'], 'Monthly',
                id='dropdown_resample',
                inline=True,
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        dcc.Graph(
            id='boxplots',
            ),

    ])

@app.callback(Output('err1', 'children'),
              Output('tbl1', 'data'),
              Input('dropdown_country', 'value'),
              Input('dropdown_resample', 'value'),
              Input('dropdown_metric1', 'value'),
              )
def update_table(value, resample, metric):

    if len(value) > MAX_COUNTRIES:
        return 'Limited to {} countries, display will be blocked until {} countr{} {} removed.'.format(MAX_COUNTRIES, len(value)-MAX_COUNTRIES, 'y' if len(value)==MAX_COUNTRIES+1 else 'ies', 'is' if len(value)==MAX_COUNTRIES+1 else 'are'), dash.no_update
    else:
        if resample == 'Monthly':
            dff = df1m.pivot(index='time', columns='name', values=metric).reset_index()
            dff.time = dff.time.dt.strftime('%B %Y')
            dff = dff.set_index('time')
            dff = dff[value].reset_index()
            dff = dff.rename(columns = {'time':'Timeframe'})
            return '', dff.to_dict("records")
        elif resample == 'Quarterly':
            dff = df1q.pivot(index='time', columns='name', values=metric).reset_index()
            dff.time = dff.time.dt.to_period(freq='Q')
            dff.time = dff.time.astype(str)
            dff = dff.set_index('time')
            dff = dff[value].reset_index()
            dff = dff.rename(columns = {'time':'Timeframe'})
            return '', dff.to_dict("records")

@app.callback(Output('err2', 'children'),
              Output('tbl2', 'data'),
              Output('tbl2', 'columns'),
              Input('dropdown_country', 'value'),
              Input('dropdown_resample', 'value'),
              Input('dropdown_metric2', 'value'),
              )
def update_table(value, resample, metric):

    if len(value) > MAX_COUNTRIES:
        return 'Limited to {} countries, display will be blocked until {} countr{} {} removed.'.format(MAX_COUNTRIES, len(value)-MAX_COUNTRIES, 'y' if len(value)==MAX_COUNTRIES+1 else 'ies', 'is' if len(value)==MAX_COUNTRIES+1 else 'are'), dash.no_update, dash.no_update
    else:
        if resample == 'Monthly':
            dff = df2m.pivot(index='time', columns='name', values=metric).reset_index()
            dff.time = dff.time.dt.strftime('%B %Y')
            dff = dff.set_index('time')
            dff = dff[value].reset_index()
            dff = dff.rename(columns = {'time':'Timeframe'})
            tblcolumns = {'name':'Timeframe','id':'Timeframe', 'type':'text'}
            listtblcolumns = [tblcolumns]
            for i in dff.columns[1:]:
                tblcolumns = listofdicts(listtblcolumns,{'name':i,'id':i,'type':'numeric', 'format':Format(precision=5, scheme=Scheme.exponent)})
            return '', dff.to_dict("records"), tblcolumns
        elif resample == 'Quarterly':
            dff = df2q.pivot(index='time', columns='name', values=metric).reset_index()
            dff.time = dff.time.dt.to_period(freq='Q')
            dff.time = dff.time.astype(str)
            dff = dff.set_index('time')
            dff = dff[value].reset_index()
            dff = dff.rename(columns = {'time':'Timeframe'})
            tblcolumns = {'name':'Timeframe','id':'Timeframe', 'type':'text'}
            listtblcolumns = [tblcolumns]
            for i in dff.columns[1:]:
                tblcolumns = listofdicts(listtblcolumns,{'name':i,'id':i,'type':'numeric', 'format':Format(precision=5, scheme=Scheme.exponent)})
            return '', dff.to_dict("records"), tblcolumns

@app.callback(Output('err4', 'children'),
              Output("boxplots", "figure"),
              Input('dropdown_country', 'value'),
              Input('dropdown_resample', 'value'),
              Input('dropdown_metric4', 'value'),
              )
def update_graph(value, resample, metric):

    if len(value) > MAX_COUNTRIES:
        return 'Limited to {} countries, display will be blocked until {} countr{} {} removed.'.format(MAX_COUNTRIES, len(value)-MAX_COUNTRIES, 'y' if len(value)==MAX_COUNTRIES+1 else 'ies', 'is' if len(value)==MAX_COUNTRIES+1 else 'are'), dash.no_update
    else:
        if resample == 'Monthly':
            dff = df4m[df4m.name.isin(value)][['name','time', metric]]
            dff = dff.rename(columns = {'name':'Country'})
            fig = px.box(dff, x=dff.Country, y=dff[metric])
            return '', fig
        elif resample == 'Quarterly':
            dff = df4q[df4q.name.isin(value)][['name','time', metric]]
            dff = dff.rename(columns = {'name':'Country'})
            fig = px.box(dff, x=dff.Country, y=dff[metric])
            return '', fig

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'),
              )
def render_content(tab):
    if tab == 'question1':
        return question1_content()
    elif tab == 'question2':
        return question2_content()
    elif tab == 'question4':
        return question4_content()

# Test server below
#if __name__ == '__main__':
#    app.run_server(debug=True)
