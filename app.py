from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

bgcolor = "#f3f3f1"  # mapbox light map land color

header = html.Div("Arapahoe Census Tract Data", className="h2 p-2 text-white bg-primary text-center")

template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

gdf = gpd.read_file('ArapahoeCT.shp')
# print(gdf)


df_SVI = pd.read_csv('Colorado_SVI.csv')
# df_SVI = df_SVI.iloc[:, []]
# print(df_SVI.columns)
col_list = list(df_SVI)
# print(col_list)
categories = list(filter(lambda x: not x.startswith('E'), col_list))
categories = categories[8:]
# print(categories)

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
    rowData=df_SVI.to_dict("records"),
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
        dbc.Row(dcc.Slider(
                id = 'opacity',
                min = 0,
                max = 1,
                value = 1,
                # marks = {i for i in range(2020,2022)}
            ),
        ),
        dbc.Row(dcc.RadioItems(
                id='radio',
                options=[
                        {'label':'S.E. Status', 'value': 'RPL_THEME1'},
                        {'label':'Household Char.', 'value': 'RPL_THEME2'},
                        {'label':'Race/Eth Minority', 'value': 'RPL_THEME3'},
                        {'label':'Housing and Transportation', 'value': 'RPL_THEME4'},
                        {'label':'Povery Flag', 'value': 'F_POV150'},
                        {'label':'Uninsured Flag', 'value': 'F_UNINSUR'},
                        {'label':'65+ Flag', 'value': 'F_AGE65'},
                        ], inline=True,
            ),
        ),
        dbc.Row(dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label': i, 'value': i} for i in categories
                ]             
            ),
        ),
        
        # dbc.Row(dbc.Col(table, className="py-4")),
        dcc.Store(id='map-data', storage_type='session'),
    ],
)

@app.callback(
    Output('map-data', 'data'),
    Input('radio', 'value'),
)
def get_data(radio):
    df = df_SVI
    print(df)
    # df = df_SVI[df_SVI[]]
    # if radio == 'S.E. Status':

    #     df = df_SVI[df_SVI['THEME'] == 1]
    return df.to_json()

@app.callback(
    Output('ct-map', 'figure'),
    Input('map-data', 'data'),
    Input('dropdown', 'value'),
    Input('opacity', 'value')
)
def get_figure(selected_data, radio, opacity):
    # sel_dict = selected_row[0]
    # del sel_dict['Label']
    # print(sel_dict)
    df = pd.read_json(selected_data)
    df['FIPS'] = df["FIPS"].astype(str)
    
    selection = radio
    
    # df2 = pd.DataFrame.from_dict(sel_dict, orient='index', columns=['Count'])
    # df2 = df2.iloc[1: , :]
    # df2.index.names = ['FIPS']
    tgdf = gdf.merge(df, on='FIPS')
    # tgdf['Count'] = tgdf['Count'].str.replace(",", "")
    # tgdf.fillna(0,inplace=True)
    # tgdf['Count'] = (tgdf['Count'].astype(int))
    tgdf = tgdf.set_index('FIPS')
    # print(tgdf)

    

    fig = px.choropleth_mapbox(tgdf, 
                                geojson=tgdf.geometry, 
                                color=selection,                               
                                locations=tgdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=opacity)

    fig.update_layout(mapbox_style="open-street-map", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')


    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)