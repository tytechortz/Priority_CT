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
print(gdf)


df_SVI = pd.read_csv('Colorado_SVI.csv')

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
        dbc.Row(dcc.RadioItems(
                id='radio',
                options=['SVI', 'Income', 'Households'], inline=True,
            ),
        ),
        dbc.Row(dbc.Col(table, className="py-4")),
        dcc.Store(id='map-data', storage_type='session'),
    ],
)

@app.callback(
    Output('map-data', 'data'),
    Input('radio', 'value'),
)
def get_data(radio):
    if radio == 'SVI':
        df = df_SVI
    return df.to_json()

@app.callback(
    Output('ct-map', 'figure'),
    Input('map-data', 'data')
)
def get_figure(selected_data):
    # sel_dict = selected_row[0]
    # del sel_dict['Label']
    # print(sel_dict)
    df = pd.read_json(selected_data)
    df['FIPS'] = df["FIPS"].astype(str)
    
    # df2 = pd.DataFrame.from_dict(sel_dict, orient='index', columns=['Count'])
    # df2 = df2.iloc[1: , :]
    # df2.index.names = ['FIPS']
    tgdf = gdf.merge(df, on='FIPS')
    # tgdf['Count'] = tgdf['Count'].str.replace(",", "")
    # tgdf.fillna(0,inplace=True)
    # tgdf['Count'] = (tgdf['Count'].astype(int))
    tgdf = tgdf.set_index('FIPS')
    print(tgdf)

    

    fig = px.choropleth_mapbox(tgdf, 
                                geojson=tgdf.geometry, 
                                color="MP_AGE65",                               
                                locations=tgdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=0.5)

    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')


    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)