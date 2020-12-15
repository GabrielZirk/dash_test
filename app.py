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
                      title = "Daily infections",
                     color = "DeltaAnzahlVortag", orientation = "v",
             color_continuous_scale = "inferno", labels = dict(Datum = "Datum", DeltaAnzahlVortag = "Neuinfektionen/Tag", sex = "Neuinfektionen/Tag")



app.layout = html.Div([
    html.H2('Data Science Rox :)'),
    dcc.Graph(id = "covid_dash",
              figure = fig_timeline)
])


if __name__ == '__main__':
    app.run_server(debug=True)