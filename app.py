import pandas as pd
import numpy as np
import os
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import plotly.express as px

from region_abbreviations import us_state_abbrev
from column_translater import ihme_column_translator


#load data
def load_projections():
    
    df = pd.read_csv(os.path.join('data','ihme_compiled.csv'))

    df['date'] = pd.to_datetime(df['date'])
    df['model_date'] = pd.to_datetime(df['model_version'].str[0:10].str.replace('_','-'))
    df['location_abbr'] = df['location_name'].map(us_state_abbrev)
    df['model_name'] = 'IHME'

    return df

def filter_df(df, model, location, metric, start_date, end_date):
    dff = df.copy()
    dff = dff[
        (dff.location_name == location) & 
        (dff.model_name == model) &
        (dff.model_date >= start_date) &
        (dff.model_date <= end_date) & 
        (dff.date > '2020-02-15') &
        (dff[metric] > 0)
        ]
    return dff

df = load_projections()

#initialize app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
title = 'COVID-19 Projections Tracker'
app.title = title
server = app.server

#controls - adapted from https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/
controls = dbc.Card(
    [
        html.H4("Filters", className="card-title"),
        dbc.FormGroup(
            [
                dbc.Label("Model"),
                dcc.Dropdown(
                    id="model-dropdown",
                    options=[
                        {"label": col, "value": col} for col in ['IHME']
                    ],
                    value="IHME",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Location"),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[
                        {"label": col, "value": col} for col in df.location_name.unique()
                    ],
                    value="United States of America",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Metric"),
                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[
                        {"label": ihme_column_translator[col], "value": col} for col in df.select_dtypes(include=np.number).columns.tolist()
                    ],
                    value="deaths_mean",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Model Date"),
                dcc.DatePickerRange(
                    id='model-date-picker',
                    min_date_allowed=df.model_date.min(),
                    max_date_allowed=datetime.today(),
                    start_date=df.model_date.min(),
                    end_date=datetime.today(),
                    initial_visible_month=datetime.today(),
                ),
            ]
        ),
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(brand=title, color="primary", dark=True),
        html.Div(dbc.Alert("Historical model projections for a given country or region (currently only supports IHME projections)", color="primary", id='alert')),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=3),
                dbc.Col(dcc.Graph(id="primary-graph"), md=9),
            ],
            align="center",
        ),
        dbc.Row(id='stat-cards')
    ],
    fluid=True,
)

@app.callback(
    Output("primary-graph", "figure"),
    [
        Input("model-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("metric-dropdown", "value"),
        Input("model-date-picker", "start_date"),
        Input("model-date-picker", "end_date")
    ],
)
def make_primary_graph(model, location, metric, start_date, end_date):

    dff = filter_df(df, model, location, metric, start_date, end_date)

    dff['model_label'] = dff['model_date'].dt.strftime("%m/%d").str[1:]

    plot_title = f'{model} - {location} - {ihme_column_translator[metric]}'
    num_models = len(dff.model_version.unique())
    sequential_color_scale = px.colors.sequential.tempo

    fig = px.line(
        dff,
        x='date',
        y=metric,
        color='model_label',
        color_discrete_sequence=sequential_color_scale[len(sequential_color_scale)-num_models:],
        title=plot_title,
        labels=ihme_column_translator,
        hover_name='model_version',
        hover_data=['model_name']
    )

    fig.layout.template = 'ggplot2'
    fig.update_layout(
        legend_title='<b>Model Date</b>',
        legend=dict(orientation='v', x=1, y=0.5),
        margin=dict(l=40, r=40, t=40, b=40),
        shapes=[
            dict(
                type= 'line',
                yref= 'paper', y0= 0, y1= 1,
                xref= 'x', x0= datetime.today(), x1= datetime.today(),
                line=dict(color="Black", width=2, dash='dashdot')
            )
        ])

    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=5000)
