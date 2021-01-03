import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.express as px

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import geojson
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

z = urlopen("https://covid19-dashboard.ages.at/data/data.zip")
covidzip = ZipFile(BytesIO(z.read())).extract("CovidFaelle_Timeline_GKZ.csv")
covf_GKZ_tl = pd.read_csv(covidzip, delimiter=";")

covf_GKZ_tl["Time"] = covf_GKZ_tl["Time"].str.slice(0, 10) # slicing the time
#covf_GKZ_tl['Time']= pd.to_datetime(covf_GKZ_tl['Time']) # converting string to datetime.timestamp
#covf_GKZ_tl['timeint'] = covf_GKZ_tl['Time'].dt.strftime("%Y%m%d").astype(int) # creating integer from timestamp

covf_GKZ_tl["timeint"] = covf_GKZ_tl["Time"].apply(lambda x: x[6:10] + x[3:5] + x[0:2])
covf_GKZ_tl["timeint"] = covf_GKZ_tl["timeint"].astype(int)

timeint_list = []
for x in range(len(covf_GKZ_tl["timeint"])):
    timeint_list.append(covf_GKZ_tl["timeint"][x])
timeint_list = list(set(timeint_list))
timeint_list.sort()

covf_GKZ_tl["timecount"] = covf_GKZ_tl["timeint"].apply(lambda x: timeint_list.index(x))

marks = dict()
# for i in range(len(covf_GKZ_tl)):
#     marks[str(covf_GKZ_tl["timecount"][i])] = covf_GKZ_tl["Time"][i]

for i in [0.99, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
    marks[str(covf_GKZ_tl["timecount"][round(len(covf_GKZ_tl) * i, 0)])] = covf_GKZ_tl["Time"][round(len(covf_GKZ_tl) * i, 0)]
#print(marks)


with open("data/Oesterreich_BEV_VGD_LAM_simple_wgs84_dissolved_BKZ.json") as f:
    austria_json = geojson.load(f)

app.layout = html.Div(children = [
    html.H3(children = """Covid19 cases over time per GKZ"""),
    dcc.Graph(id = "graph_with_slider",
              responsive = "auto",
              style = {"height" : "60vh"}),
    dcc.Slider(id = "date-slider",
               min = covf_GKZ_tl["timecount"].min(),
               max = covf_GKZ_tl["timecount"].max(),
               value = covf_GKZ_tl["timecount"].min(),
               marks = marks,
               step = 1)])



@app.callback(
    Output('graph_with_slider', 'figure'),
    Input('date-slider', 'value'))


def update_figure(selected_date):
    filtered_covf_GKZ_tl = covf_GKZ_tl[covf_GKZ_tl.timecount == selected_date]

    austria_choropleth_cases = px.choropleth_mapbox(filtered_covf_GKZ_tl, geojson = austria_json, color = "AnzahlFaelleSum",
                                                    locations = "GKZ", featureidkey = "properties.BKZ",
                                                    color_continuous_scale = "Viridis",
                                                    center = {"lat" : 47.6964719, "lon" : 13.3457347},
                                                    mapbox_style = "carto-positron", zoom = 6,
                                                    range_color = (0, 6000),
                                                    opacity = 0.5,
                                                    labels={"AnzahlFaelleSum" : "Covid19 cases"},
                                                    hover_data = ["Bezirk"])

    austria_choropleth_cases.update_layout(coloraxis_colorbar = dict(tickmode = "array",
                                                                     tickvals = [0, 1000, 2000, 3000, 4000, 5000, 6000],
                                                                     ticktext = ["0", "1000", "2000", "3000", "4000", "5000", "> 6000"]),
                                           transition_duration = 500)

    return austria_choropleth_cases


if __name__ == '__main__':
    app.run_server(debug=True)