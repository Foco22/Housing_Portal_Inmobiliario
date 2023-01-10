import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import numpy  as np
import dash_daq as daq
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from dash import Dash, dash_table
import dash_table_experiments as dt
import requests
import pyshorteners as sh
import time
from google.cloud import storage
import plotly.graph_objs as go
import dash_html_components as html

########################## INICIO APP ####################################

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])


######################### PARAMETROS #####################################

colors = {
    'background': '#f2f2f2',
    'text':  '#292929'
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 1,
    "left": 0,
    "bottom": 0,
    "width": "30rem",
    "padding": "5rem 2rem",
    "background-color": '#f9f9f9',
    'color': colors['text']
}

theme = {
    "background-color": '#1e2130',
    'detail': '#25ec00',  # Background-card
    'primary': '#25ec00',  # Green
    'secondary': '#FFD15F',  # Accent
}



def metro_rango(x):

    if x > 10 and x < 30:
        return '10-30'
    elif x >= 30 and x <= 60:
        return '30-60'
    elif x > 60 and x <= 100:
        return '60-100'
    elif x > 100:
        return '100-1000'

def precio_rango(x):

    if x > 200000 and x < 400000:
        return '200.000-400.000'
    elif x >= 400000 and x <= 700000:
        return '400.000-700.000'
    elif x > 700000 and x <= 1000000:
        return '700.000-1.000.000'
    elif x > 1000000:
        return '>1.000.000'



######################### CARGA DE DATOS #################################


def base_input():
    
    storage_client = storage.Client.from_service_account_json("ferrous-pact-273022-63f668492a23.json")
    bucket = storage_client.list_blobs('portal_inmobiliario_proyecto')

    nombre_archivos = []
    for blob in bucket:
       x = blob.name
       x = x.split('_Venta_')[1].split(' ')[0]
       nombre_archivos.append(x)

    nombre_archivos.sort()
    fecha_file = nombre_archivos[-1]

    bucket = storage_client.list_blobs('portal_inmobiliario_proyecto')
    for blob in bucket:
        if fecha_file in blob.name:
           nombre_file = blob.name
    
    df = pd.read_csv('gs://portal_inmobiliario_proyecto/{}'.format(nombre_file),sep = ';', storage_options={"token": "ferrous-pact-273022-63f668492a23.json"})


    df = df.loc[df['Letra'] == 'RM']
    df = df.loc[df['tipo'] == 'arriendos']
    df = df.loc[df['monto'] > 200000]
    df = df.loc[df['monto'] < 2000000]
    df = df.loc[df['dormitorios'] < 7]
    df['rango_metros'] = df['metros'].apply(lambda x : metro_rango(x))
    df['precio_rango'] = df['monto'].apply(lambda x : precio_rango(x))
    df = df.rename(columns = {'lng':'lon'})
    df['Fecha Reporte'] = df['fecha'].apply(lambda x : str(x)[:10])
    df = df.reset_index().drop(columns =['index'])
    df['Arriendo ($)'] = df['monto']
    df['direccion'] = df['direccion'].apply(lambda x : str(x.split(',')[0]))

    df['Arriendo/Metro'] = df['monto']/df['metros']


    return df


df = base_input()
comunas_dic = {}

fecha_update = df['Fecha Reporte'][0]

for x in list(df['comuna'].unique()):
    comunas_dic[x] = x

metro_dic = {}

for x in list(df['rango_metros'].unique()):
    metro_dic[x] = x


habit_dic = {}

for x in list(df['dormitorios'].unique()):
    habit_dic[x] = x

monto_dic = {}

for x in list(df['precio_rango'].unique()):
    monto_dic[x] = x



df['Link Portal Inmobiliario'] = df['Link'].apply(lambda x : "[PortalInmobiliario]("+ x + ")")


######################## FUNCIONES #######################################


options=[{"label": i, "value": i} for i in comunas_dic]



def sider_funcion():

    sidebar = html.Div(id='filtros', className ='side_bar_mobile', children = [html.Div(
    [   #html.Div(children = [html.Img(src=app.get_asset_url('descarga.png'),style={'max-height':'100%', 'max-width':'100%','display': 'inline'})]),
        html.Br(),
        html.Br(),
        html.P(
            "Update: {} ".format(fecha_update), style = {'front size': '0.5px'}
        ),
        html.H2("FILTROS",style = {'color': 'black'}),
        html.Hr(),
        dbc.Label("Rango de Arriendo (CLP)", html_for="n-guests"), 
        dcc.Dropdown(
                            id="Arriendo",
                            options=[{"label": i, "value": i} for i in monto_dic],
                            placeholder="Seleccionar Arriendo",
                            multi=True,
                            style ={'backgroundColor':  '#f2f2f2','color':'black',
                                        'width':'25vH','height':'40px'},
                            #value=[1,2,3,4]
                        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Label("Habitaciones", html_for="n-guests"), 
        dcc.Dropdown(
                            id="Habitaciones",
                            options=[{"label": i, "value": i} for i in habit_dic],
                            placeholder="Seleccionar habitaciones",
                            multi=True,
                            style ={'backgroundColor':  '#f2f2f2','color':'black',
                                        'width':'25vH','height':'40px'},
                            #value=[1,2,3,4]
                        ),
        html.Br(),
        dbc.Label("Rango de Metros (m2) ", html_for="n-guests"), 
        dcc.Dropdown(
                            id="metro",
                            options=[{"label": i, "value": i} for i in metro_dic],
                            placeholder="Seleccionar metros (m2)",
                            multi=True,
                            style ={'backgroundColor':  '#f2f2f2','color':'black',
                                        'width':'25vH','height':'40px'},
                            #value=['10-30','30-60','60-100','100-1000']
                        ),
        html.Br(),
        html.Br(),
        dbc.Label("Comunas", html_for="n-guests"), 
        dcc.Dropdown(
                            id="Comunas",
                            options=[{"label": i, "value": i} for i in comunas_dic],
                            placeholder="Seleccionar comunas",
                            multi=True,
                            style ={'backgroundColor': '#f2f2f2','color':'black',
                                        'width':'25vH','height':'40px'},
                            #value=['Las Condes','Vitacura','Providencia','Santiago']

                        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(children = [html.Img(src=app.get_asset_url('logo_linkedin.png'),style={'max-height':'7%', 'max-width':'7%','display': 'inline'}), 
                             html.P('s', style={'color': 'white', 'display':'inline-block','textAlign': 'left'}),
                             html.P('   Linkedin', style={'color': 'black', 'display':'inline-block','textAlign': 'right'})]),
        html.Div(children = [html.A(href='https://rb.gy/ylgzkw', children='https://rb.gy/ylgzkw', target='_blank')]),                     
        html.Br(),
        html.Div(children = [html.Img(src=app.get_asset_url('github.png'),style={'max-height':'10%', 'max-width':'10%','display': 'inline'}), 
                             html.P('s', style={'color': 'white', 'display':'inline-block','textAlign': 'left'}),
                             html.P('   Github', style={'color': 'black', 'display':'inline-block','textAlign': 'left'})]),
        html.Div(children = [html.A(href='https://github.com/Foco22', children='https://github.com/Foco22', target='_blank')]),  
    ],
    style=SIDEBAR_STYLE,
)
])

    return sidebar



def dormitorio_filtrado():



    return html.Div(children = [html.P("Mínimo (CLP)", style = {'font_family': 'TITILLIUM SANS'}), html.H2(id = "dormitorios_filter",style = {'color':'black','size': 10})],
                                    id="total_filter",
                                    className="mini_container",
                                    style ={'width':'20vH','height':'150px', 'font_size': 1000}

                                )


def comunas_filtrados():

    return html.Div(children = [html.P("Promedio (CLP)", style = {'color':'black','font_size': 50}), html.H2(id = "comunas_filtrados",style = {'color':'black','size': 10})],
                                    id="total_filter",
                                    className="mini_container",
                                    style ={'width':'20vH','height':'150px', 'font_size': 1000}

                                )


def metro_filtrados():

    return html.Div(children = [html.P("Maximo (CLP)", style = {'color':'black','font_size': 50}), html.H2(id = "metro_filtrados",style = {'color':'black','size': 10})],
                                    id="total_filter",
                                    className="mini_container",
                                    style ={'width':'20vH','height':'150px', 'font_size': 1000}

                                )




def scatter_figure_plot():

    return html.Div(
        id="quick-stats",
        className='pretty_container',
        children=[dcc.Loading(dcc.Graph(id='scatter_figure'))]
    )

def box_figure_plot():

    return html.Div(
        id="quick-stats",
        className='pretty_container',
        children=[dcc.Loading(dcc.Graph(id='box_figure'))]
    )


def bar_figure_plot():

    return html.Div(
        id="quick-stats",
        className='pretty_container',
        children=[dcc.Loading(dcc.Graph(id='barplot_figure'))]
    )


df_table = df[['direccion','metros','dormitorios','comuna', 'Arriendo ($)', 'Link Portal Inmobiliario','Fecha Reporte']]

PAGE_SIZE = 0

def generate_table():
    return  html.Div(
        id="quick-stats",
        className='pretty_container',
        children=[dash_table.DataTable(
    id='table-container',
    #columns=[
    #    {"name": i, "id": i} for i in sorted(df_table.columns)
    #],
    columns=[{'name': x, 'id': x, 'presentation': 'markdown'} if x == 'Link Portal Inmobiliario' else {'name': x, 'id': x} for x in df_table.columns],
    data=df_table.to_dict('records'),
    page_current=0,
    page_size=PAGE_SIZE,
    page_action='custom',
    fixed_rows = {'headers':True, 'data':0},
    #style_header={'textAlign': 'center'},
    style_header={'padding':'5px','textAlign': 'center','color':'black','minWidth': '20px','backgroundColor':'#0000B7','color':'#FFFFFF'},
    style_cell={'textAlign':'center','minWidth': 95, 'maxWidth': 200, 'width': 152,'font_size': '12px','whiteSpace':'normal','height':'auto'}

)]
    )

columns=[{'name': x, 'id': x, 'presentation': 'markdown'} if x == 'Link Portal Inmobiliario' else {'name': x, 'id': x} for x in df.columns],



###################  CALLBACK ###################################


@app.callback(
    Output(component_id='dormitorios_filter', component_property='children'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_dormitorio(dormitorios_select,comuna_select,metro_select, precio_select):
    
    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]

    return filtered_df['monto'].min()


@app.callback(
    Output(component_id='comunas_filtrados', component_property='children'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)



def update_figure_comuna(dormitorios_select,comuna_select,metro_select,precio_select):
    

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]


    if math.isnan(filtered_df['monto'].mean()) == False:
         valor = int(filtered_df['monto'].mean())
    else:
        valor = filtered_df['monto'].mean()

    return valor

@app.callback(
    Output(component_id='metro_filtrados', component_property='children'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_metro(dormitorios_select,comuna_select,metro_select,precio_select):
    
    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]


    return filtered_df['monto'].max()



graph_config = {'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}

def mapa_figure_2():

    #return html.Div(children = [dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True})],className='pretty_container')
    
    return dbc.Spinner(children = [dcc.Loading(dcc.Graph(
            id='graph',className='pretty_container'
        ))])
    


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)




def update_figure_mapa(dormitorios_select,comuna_select,metro_select,precio_select):

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]
    
    margin={"l": 0, "r": 0, "b": 0, "t": 50}

    
    fig = px.box(filtered_df, x="dormitorios", y="monto" ,title="Distribución arriendo por cantidad de dormitorios",labels={'comuna': '', 'monto':''})

    fig.update_layout(
    title_font_family="sans-serif",
    autosize=False,
    width=500,
    height=450,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9")
    
    
    fig.update_layout(
    title_x=0.5,
    title_y=0.99,
    margin={"l": 0, "r": 0, "b": 0, "t": 50}
)


    return fig



 

@app.callback(
    Output(component_id='scatter_figure', component_property='figure'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_scatterplot(dormitorios_select,comuna_select,metro_select,precio_select):
    

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())



    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]

    fig = px.scatter(filtered_df, x="metros", y="monto", trendline="ols",title="Relación Precio Arriendo por Metro cuadrado",labels={'metros': '', 'monto':''})

    fig.update_layout(
    title_font_family="sans-serif",
    autosize=False,
    width=500,
    height=450,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9")
    
    
    fig.update_layout(
    title_x=0.5,
    title_y=0.99,
    margin={"l": 0, "r": 0, "b": 0, "t": 50}
)

    return fig


@app.callback(
    Output(component_id='box_figure', component_property='figure'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_boxplot(dormitorios_select,comuna_select,metro_select,precio_select):
    

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]

    fig = px.box(filtered_df, x="comuna", y="monto" ,title="Distribución del Arriendo según comuna",labels={'comuna': '', 'monto':''})


    fig.update_layout(
    title_font_family="sans-serif",
    autosize=False,
    width=1080,
    height=400,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9")
    
    fig.update_layout(
    title_x=0.5,
    title_y=0.95,
    margin={"l": 0, "r": 0, "b": 0, "t": 50},
    #title_font_family="sans-serif",
    font_family="sans-serif"
    
)

    fig.update_yaxes(matches=None)
    fig.update_yaxes(visible=True)
    

    return fig



@app.callback(
    Output(component_id='table-container', component_property='data'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_table(dormitorios_select,comuna_select,metro_select,precio_select):
    

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())

    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]

    
    filtered_df = filtered_df[['Arriendo ($)','metros','dormitorios','direccion','Link Portal Inmobiliario','comuna','Fecha Reporte']]
     
    df_vacio = pd.DataFrame(columns = ['Arriendo ($)','metros','dormitorios','direccion','Link Portal Inmobiliario','comuna','Fecha Reporte'])
    
    
    filtered_df = filtered_df.sort_values(by = 'Arriendo ($)',ascending= True)
    
    if len(filtered_df) < 16:
        
        for x in range(16-len(filtered_df)):
            tupla = ('','','','','','','')
            df_vacio = df_vacio.append([tupla])

        filtered_df = pd.concat([filtered_df,df_vacio], axis = 0)
    return filtered_df.to_dict("rows")


@app.callback(
    Output(component_id='barplot_figure', component_property='figure'),
    [Input(component_id='Habitaciones', component_property='value'),
    Input(component_id='Comunas', component_property='value'),
    Input(component_id='metro', component_property='value'),
    Input(component_id='Arriendo', component_property='value')]
)

def update_figure_barplot(dormitorios_select,comuna_select,metro_select,precio_select):
    

    if comuna_select == None or len(comuna_select) == 0:
        comuna_select = list(df['comuna'].unique())
    if dormitorios_select == None or len(dormitorios_select) == 0:
        dormitorios_select = list(df['dormitorios'].unique())
    if metro_select == None or len(metro_select) == 0:
        metro_select = list(df['rango_metros'].unique())
    if precio_select == None or len(precio_select) == 0:
        precio_select = list(df['precio_rango'].unique())


    filtered_df = df[df.dormitorios.isin(dormitorios_select)]
    filtered_df = filtered_df.loc[filtered_df['comuna'].isin(comuna_select)]
    filtered_df = filtered_df.loc[filtered_df['rango_metros'].isin(metro_select)]
    filtered_df = filtered_df.loc[filtered_df['precio_rango'].isin(precio_select)]
    

    filtered_df = filtered_df.groupby(['comuna']).mean()['Arriendo/Metro'].reset_index()
    
    filtered_df = filtered_df.sort_values(by = 'Arriendo/Metro', ascending = False)

    fig = px.bar(filtered_df, x="comuna", y="Arriendo/Metro" ,title="Ratio de Arriendo promedio / Metros cuadrados según comuna",labels={'comuna': '', 'Arriendo/Metro':''}, text_auto='.3s')
    
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    fig.update_layout(
    title_font_family="sans-serif",
    autosize=False,
    width=1080,
    height=400,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9")
    
    fig.update_layout(
    title_x=0.5,
    title_y=0.95,
    margin={"l": 0, "r": 0, "b": 0, "t": 50},
    #title_font_family="sans-serif",
    font_family="sans-serif"
    
)

    fig.update_yaxes(matches=None)
    fig.update_yaxes(visible=True)
    return fig



app.layout = html.Div(style={'border': '1px solid white'}, children = [html.Div(style={'backgroundColor': colors['background']}, children = [
                dbc.Row([
                    dbc.Col(),
                    dbc.Col(),
                    dbc.Col(html.H3('Según el Portal Inmobiliario, ¿Cómo se comporta el arriendo en Santiago?',style = {'color':'black'}),width = 9, style = {'margin-left':'20px','margin-top':'30px','color': 'white', 'with': '60px',"margin-bottom": "0px"})
                    ]),
                dbc.Row([
                    dbc.Col(),
                    dbc.Col(html.H2('',style = {'color':'white'}),width = 9, style = {'margin-left':'1px','margin-top':'1px','color': 'white'})
                    ]),
                dbc.Row(
                    [dbc.Col(sider_funcion()),
                    dbc.Col(dormitorio_filtrado()),
                    dbc.Col(comunas_filtrados()),
                    dbc.Col(metro_filtrados()),
                    ]),
                dbc.Row([
                    dbc.Col(),
                    dbc.Col(html.H2('',style = {'color':'white'}),width = 9, style = {'margin-left':'1px','margin-top':'1px','color': 'white'})
                    ]),
                dbc.Row([
                    dbc.Col(),
                    dbc.Col(html.H2('',style = {'color':'white'}),width = 9, style = {'margin-left':'1px','margin-top':'1px','color': 'white'})
                    ]),
                dbc.Row([dbc.Col(sider_funcion()),
                    dbc.Col(),
                    dbc.Col(bar_figure_plot()),
                    dbc.Col()                    
                    ]),
                dbc.Row([dbc.Col(sider_funcion()),
                    dbc.Col(),
                    dbc.Col(box_figure_plot()),
                    dbc.Col()                    
                    ]),
                dbc.Row([dbc.Col(sider_funcion()),
                    dbc.Col(),
                    dbc.Col(scatter_figure_plot()),
                    dbc.Col(mapa_figure_2()),                  
                    dbc.Col()
                    ]),
                dbc.Row([dbc.Col(sider_funcion()),
                    dbc.Col(),          
                    dbc.Col(generate_table()),               
                    dbc.Col()
                    ])
    ]),
])



if __name__ == "__main__":
    app.run_server(debug=True,host="0.0.0.0",port=8080)





        