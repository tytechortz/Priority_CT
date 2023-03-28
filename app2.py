from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag


app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

bgcolor = "#f3f3f1"  # mapbox light map land color

header = html.Div("Arapahoe Census Tract Data", className="h2 p-2 text-white bg-primary text-center")

template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

gdf = gpd.read_file('ArapahoeCT.shp')
# print(gdf)


df_SVI_2020 = pd.read_csv('Colorado_SVI_2020.csv')
df_SVI_2018 = pd.read_csv('Colorado_SVI_2018.csv')
df_SVI_2016 = pd.read_csv('Colorado_SVI_2016.csv')

col_list = list(df_SVI_2020)


columnDefs = [
    {
        'headerName': 'Census Tract',
        'field': 'FIPS'
    },
]

defaultColDef = {
    "filter": True,
    "resizable": True,
    "sortable": True,
    "editable": False,
    "floatingFilter": True,
    "minWidth": 125
}

table = dag.AgGrid(
    id='ct-grid',
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=df_SVI_2020.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    # cellStyle=cellStyle,
    # dangerously_allow_code=True,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "single"},
)

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


app.layout = dbc.Container(
    [
        header,
        dbc.Row(dcc.Graph(id='ct-map', figure=blank_fig(500))),
        dbc.Row([
            dbc.Col([
                dcc.Slider(
                    id = 'opacity',
                    min = 0,
                    max = 1,
                    value = 1,
                ),
            ], width=6),
            dbc.Col([
                dcc.Slider(2016, 2020, value=2020,
                    marks={
                        2016: {'label': '2016', 'style': {'color': 'white'}},
                        2018: {'label': '2018', 'style': {'color': 'white'}},
                        2020: {'label': '2020', 'style': {'color': 'white'}},
                    },
                    id = 'year',
                ),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.RadioItems(
                    id='category-radio',
                    options=[
                        {'label': 'Total', 'value': 'E_'},
                        {'label': 'Pct.', 'value': 'EP_'},
                        {'label': 'Percentile', 'value': 'EPL_'},
                        {'label': 'Flag', 'value': 'F_'},
                    ] 
                ),
            ], width=6),
            dbc.Col([
                dcc.Dropdown(
                    id='variable-dropdown',
                ),
            ], width=6)
        ]),
        # dbc.Row(dbc.Col(table, className="py-4")),
        dcc.Store(id='map-data', storage_type='session'),
    ],
)


@app.callback(
        Output('variable-dropdown', 'options'),
        Input('category-radio', 'value')
)
def category_options(selected_value):
    print(selected_value)
    # variables = list(lambda x: x, col_list)
    variables = [{'label': i, 'value': i} for i in list(filter(lambda x: x.startswith(selected_value), col_list))]
    # print([{'label': i, 'value': i} for i in col_list[filter(lambda x: x.startswith(selected_value))]])
    return variables 

@app.callback(
    Output('map-data', 'data'),
    Input('variable-dropdown', 'value'),
)
def get_data(radio):

    df_2020 = df_SVI_2020.loc[df_SVI_2020['COUNTY'] == 'Arapahoe']
    df_2018 = df_SVI_2018.loc[df_SVI_2018['COUNTY'] == 'Arapahoe']
   
    return df_2020.to_json()

@app.callback(
    Output('ct-map', 'figure'),
    Input('map-data', 'data'),
    Input('variable-dropdown', 'value'),
    Input('opacity', 'value')
)
def get_figure(selected_data, dropdown, opacity):
  
    df = pd.read_json(selected_data)
    df['FIPS'] = df["FIPS"].astype(str)
    
    selection = dropdown
    
    tgdf = gdf.merge(df, on='FIPS')
   
    tgdf = tgdf.set_index('FIPS')
  

    fig = px.choropleth_mapbox(tgdf, 
                                geojson=tgdf.geometry, 
                                color=selection,                               
                                locations=tgdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=opacity)

    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')


    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)