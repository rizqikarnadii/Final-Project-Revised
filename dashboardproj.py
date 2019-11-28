import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_table
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

engine = create_engine('mysql+mysqlconnector://root:def321@localhost/test?host=127.0.0.1?port=3306')
conn = engine.connect()
df=pd.DataFrame(conn.execute('SELECT * FROM dashboard.vgsales;').fetchall(),columns=pd.read_csv('vgsales.csv').columns)

dropdwn=['All',*[str(i) for i in df['Platform'].unique()]]

app.layout = html.Div(children = [
    html.H1('Dashboard Final Project Video Game Sales'),
    html.P('Created by: rizqi'),
    dcc.Tabs(value = 'tabs', id = 'tabs-1', children = [
        

        dcc.Tab(label = 'Table', id = 'table', children = [
            html.Center(html.H1('DASHBOARD VG SALES')),
            html.Div(className = 'col-6', children=[
                html.P('Platform'),
                dcc.Dropdown(id= 'table-dropdown', value = 'All',
                    options= [
                        {'label': i, 'value': i} for i in dropdwn
                    ]
                )
            ]),
            html.Div(className = 'col-3', children=[
                html.P('Max Rows:'),
                dcc.Input(
                    id='page-size',
                    type='number',
                    value=10,
                    min=3,max=20,step=1
                )
            ]),
            html.Div(className = 'col-12', children = [
                html.Button(id='Search', n_clicks=0, children='Search',style={
                    'margin-top':'14px',
                    'margin-bottom':'14px'})
            ]),
            html.Div(id='div-table',className = 'col-12', children = [
                dash_table.DataTable(
                    id= 'dataTable',
                    data= df.to_dict('records'),
                    columns= [{'id': i, 'name': i} for i in df.columns],
                    page_action= 'native',
                    page_current= 0,
                    page_size = 10,
                    style_table={'overflowX': 'scroll'}
                )
            ])
        ]), 
        
        dcc.Tab(label = 'Bar Chart', id = 'bar', children = [
            html.Div(className = 'col-12', children = [
                html.Div(className = 'row', children = [
                    html.Div(className = 'col-4',children= [
                        html.P(f'Y1'),
                        dcc.Dropdown(id= f'y-axis-1', value = f'Publisher',
                            options= [
                                {'label': i, 'value': i} for i in df.select_dtypes('number').columns
                            ]
                        )
                    ]),
                    html.Div(className = 'col-4',children= [
                        html.P(f'Y2'),
                        dcc.Dropdown(id= f'y-axis-2', value = f'Platform',
                            options= [
                                {'label': i, 'value': i} for i in df.select_dtypes('number').columns
                            ]
                        )
                    ]),
                    html.Div(className = 'col-4',children= [
                        html.P(f'X'),
                        dcc.Dropdown(id= f'y-axis-3', value = f'Global_Sales',
                            options= [
                                {'label': i, 'value': i} for i in ['Global_Sales','NA_Sales','EU_Sales','JP_Sales','Other_Sales']
                            ]
                        )
                    ])
                ]),
                html.Div(children= [dcc.Graph(
                    id = 'contoh-graph-bar',
                    figure={'data' : [{
                        'x': df['Global_Sales'],
                        'y': df['Publisher'],
                        'type': 'bar',
                        'name': 'Publisher'
                    },{
                        'x': df['Global_Sales'],
                        'y': df['Platform'],
                        'type': 'bar',
                        'name': 'Platform'
                    }],
                        'layout': {'title': 'Bar Chart'}
                    }
                )])
            ])
        ]),
    
        dcc.Tab(label = 'Scatter Chart', id = 'scatter', children = [
        html.Div(children = dcc.Graph(
            id = 'graph-scatter',
            figure = {'data':[go.Scatter(
                x= df[df['Global_Sales']==i]['Rank'],
                y= df[df['Global_Sales']==i]['Global_Sales'],
                text= df[df['Global_Sales']==i]['Rank'],
                mode='markers',
                name= f'{i}'    
            ) for i in df['Global_Sales'].unique()
            ],
                'layout':go.Layout(
                    xaxis= {'title':'Rank'},
                    yaxis = {'title' : 'Publisher'},
                    hovermode = 'closest'
                )
            }
        ),className = 'col-12')
    ]),

    dcc.Tab(label = 'Pie Chart', id = 'tab-dua', children = [
        html.Div(className = 'col-4',children= [
            html.P('Select value'),
            dcc.Dropdown(id= f'pie-dropdown', value = 'Other_Sales',
                options= [
                    {'label': i, 'value': i} for i in df.select_dtypes('number').columns
                ]
            )
        ]),
        html.Div(className = 'col-12', children = dcc.Graph(
            id = 'pie-chart',
            figure= {'data' : [go.Pie(
                labels=list(i for i in df['Platform'].unique()),
                values=list(df.groupby('Platform').mean()['Other_Sales'])
            )
            ], 'layout': {'title': 'Pie Chart w/mean'},}
        ))
    ])
    
    ],
        content_style = {
            'fontFamily': 'Arial',
            'borderBottom': '1px solid #d6d6d6',
            'borderRight': '1px solid #d6d6d6',
            'borderLeft': '1px solid #d6d6d6',
            'padding': '44px'
        },
        className = 'row'
    )
], 
    style={
        'maxwidth': '1200px', 'margin': '0 auto'
    }
)

@app.callback(
    Output(component_id= 'contoh-graph-bar', component_property= 'figure'),
    [Input(component_id=f'y-axis-{i}', component_property='value') for i in range(1,4)]
)
def create_graph_bar(y1,y2,x):
    figure={'data' : [{
        'x': df[x],
        'y': df[y1],
        'type': 'bar',
        'name': y1
    },{
        'x': df[x],
        'y': df[y2],
        'type': 'bar',
        'name': y2
    }]
        
    }
    return figure

@app.callback(
    Output(component_id= 'pie-chart', component_property= 'figure'),
    [Input(component_id=f'pie-dropdown', component_property='value')]
)
def create_pie_chart(pie):
    figure= {'data' : [go.Pie(
            labels=list(i for i in df['Platform'].unique()),
            values=list(df.groupby('Platform').mean()[pie])
        )
        ], 'layout': {'title': 'Mean Pie Chart'}
    }
    return figure

@app.callback(
    Output(component_id= 'dataTable', component_property= 'data'),
    [Input(component_id='Search', component_property='n_clicks')],
    [State(component_id='table-dropdown',component_property='value')]
)

def update_data(n_clicks,global_sales):
    if fuel_type == 'All':
        df = df.to_dict('records')
    else:
        df = df[df['Global_Sales']==Global_Sales].to_dict('records')
    return df

@app.callback(
    Output(component_id= 'dataTable', component_property= 'page_size'),
    [Input(component_id='Search', component_property='n_clicks')],
    [State(component_id='page-size',component_property='value')]
)

def update_data(n_clicks,size):
    return size

if __name__ == '__main__':
    app.run_server(debug=True)