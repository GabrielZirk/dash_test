import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.express as px

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import geojson

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


z = urlopen("https://covid19-dashboard.ages.at/data/data.zip")
covidzip = ZipFile(BytesIO(z.read())).extract("CovidFaelleDelta.csv")
covf_delta = pd.read_csv(covidzip, delimiter=";")


covf_delta["Datum"] = covf_delta.Datum.str[0:10]

fig_timeline = px.bar(covf_delta,
                      x="Datum",
                      y = "DeltaAnzahlVortag",
                     color = "DeltaAnzahlVortag", orientation = "v",
             color_continuous_scale = "inferno", labels = dict(Datum = "Datum", DeltaAnzahlVortag = "Neuinfektionen/Tag", sex = "Neuinfektionen/Tag"))

fig_timeline.update_layout(xaxis = dict(
        tickmode = 'linear',
        dtick = 10
    ))
########################
z = urlopen("https://covid19-dashboard.ages.at/data/data.zip")
covidzip = ZipFile(BytesIO(z.read())).extract("CovidFaelle_Altersgruppe.csv")
covf_ag = pd.read_csv(covidzip, delimiter=";")

covf_ag_oe = covf_ag[covf_ag["Bundesland"] == "Österreich"]

fig_agegroup_mw_cases = px.bar(covf_ag_oe,
                        x = "Altersgruppe",
                        y = "Anzahl",
                        color = "Geschlecht",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        template = "ggplot2")

fig_agegroup_mw_cases.update_layout(title = {"xanchor" : "left"})
###################################
fig_agegroup_mw_death = px.bar(covf_ag_oe,
                        x = "Altersgruppe",
                        y = "AnzahlTot",
                        color = "Geschlecht",
                        barmode = "group",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        text = "AnzahlTot",
                        template = "ggplot2")
fig_agegroup_mw_death.update_traces(texttemplate = '%{text:.3s}', textposition ='outside')
fig_agegroup_mw_death.update_layout(uniformtext_minsize = 4, uniformtext_mode ='hide')
####################################
z = urlopen("https://covid19-dashboard.ages.at/data/data.zip")
covidzip = ZipFile(BytesIO(z.read())).extract("CovidFaelle_Timeline.csv")
covf_epik = pd.read_csv(covidzip, delimiter=";")

covf_epik_at = covf_epik[covf_epik["Bundesland"] == "Österreich"]

covf_epik_at["Time"] = covf_epik_at.Time.str[0:10]

fig_covf_epik = go.Figure()

fig_covf_epik.add_trace(go.Scatter(x = covf_epik_at["Time"],
                                  y = covf_epik_at["AnzahlFaelleSum"],
                                  mode = "lines",
                                   name = "Kumm. Anzahl Fälle",
                                  fill = "tozeroy",
                                   marker = dict(color = "LightSkyBlue")))

fig_covf_epik.add_trace(go.Scatter(x = covf_epik_at["Time"],
                                  y = covf_epik_at["AnzahlGeheiltSum"],
                                  mode = "lines",
                                   name = "Kumm. Anzahl Geheilte",
                                  fill='tozeroy',
                                  marker = dict(color = "green")))

fig_covf_epik.add_trace(go.Scatter(x = covf_epik_at["Time"],
                                  y = covf_epik_at["AnzahlTotSum"],
                                  mode = "lines",
                                   name = "Kumm. Anzahl Tote",
                                  fill = "tozeroy",
                                  marker = dict(color = "red")))

fig_covf_epik.update_layout(xaxis = dict( tickmode = 'linear',
                                         dtick = 10,
                                        tickangle=45),
                                        template = "ggplot2")
#####################################################################

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

app.layout = html.Div(children=[
    html.H1('Data Science Rox :)'),
    html.H3(children = """Covid19 cases over time per GKZ"""),
    dcc.Graph(id = "graph_with_slider",
              responsive = "auto",
              style = {"height" : "60vh"}),
    dcc.Slider(id = "date-slider",
               min = covf_GKZ_tl["timecount"].min(),
               max = covf_GKZ_tl["timecount"].max(),
               value = covf_GKZ_tl["timecount"].min(),
               marks = marks,
               step = 1),


    html.H3(children = """Tägliche Neuinfektionen"""),
    dcc.Graph(id = "Timeline Cases",
              figure = fig_timeline),

    html.H3(children = """Anzahl Erkrankter nach Altersgruppe"""),
    dcc.Graph(id = "Cases by agegroup",
              figure = fig_agegroup_mw_cases),

    html.H3(children = """Anzahl Tote nach Altersgruppe"""),
    dcc.Graph(id = "Deaths by agegroup",
              figure = fig_agegroup_mw_death),

    html.H3(children = """Epikurven"""),
    dcc.Graph(id = "epicurve",
              figure = fig_covf_epik)

])



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