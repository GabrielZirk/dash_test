import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.express as px

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

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


app.layout = html.Div(children=[
    html.H1('Data Science Rox :)'),
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


if __name__ == '__main__':
    app.run_server(debug=True)