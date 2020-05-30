#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from collections.abc import Iterable

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_talisman import Talisman

import plotly.graph_objects as go
import plotly.express as px

from region_abbreviations import us_state_abbrev
from more_info import more_info_alert
from column_translater import column_translator
from plot_option_data import csv_dtypes, table_dtypes
from config import app_config, plotly_config

# make sqlite connection
engine = create_engine(app_config['sqlalchemy_database_uri'])
table_name = app_config['database_name']

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

def unique_location_names():
    df = pd.read_sql_query("SELECT DISTINCT location_name FROM projections", engine)
    return list(flatten(df.values))

def min_model_date():
    df = pd.read_sql_query("SELECT MIN(model_date) FROM projections", engine)
    return df.iloc[0,0]

def metric_labels():
    df = pd.read_sql_query("SELECT * FROM projections limit 10", engine)
    df = df.astype(dict((k, table_dtypes[k]) for k in df.columns if k in table_dtypes))
    return sorted([{"label": column_translator[col], "value": col} for col in df.select_dtypes(include=np.number).columns.sort_values().tolist() ], key=lambda k: k['label'])

def filter_df(model, location, metric, start_date, end_date):

    filter_query = "SELECT location_name, date, {3}, model_name, model_date, model_version, location_abbr FROM {0} WHERE {0}.location_name = {1} AND {0}.model_name IN ({2}) AND {0}.model_date BETWEEN {1} AND {1} AND {0}.date > '2020-02-15' AND {0}.date < '2020-07-15' ORDER BY {0}.date"
    filter_query = filter_query.format(table_name,'%s', ','.join(['%s'] * len(model)), metric)

    dff = pd.read_sql_query(filter_query,engine, params=tuple(flatten((location, model, start_date, end_date))),
                            parse_dates=['model_date', 'date'])


    # there's probably a better way to do this instead of hard-coding the types
    dff = dff.astype(dict((k, table_dtypes[k]) for k in dff.columns if k in table_dtypes))

    dff.dropna(subset=[metric], inplace=True)

    dff['model_label'] = dff['model_name'].astype('str') + '-' + dff['model_date'].dt.strftime("%m/%d").str[1:]
    dff['model_name'] = dff['model_name'].astype('str')
    dff = dff.sort_values(['model_label','date'])

    return dff

#initialize app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP,
                          {
                                'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
                                'rel': 'stylesheet',
                                'crossorigin': 'anonymous'
                            }
                          ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
title = 'COVID Projections Tracker'
app.title = title
server = app.server #need this for heroku - gunicorn deploy

# This forces https for the site
if not app_config['debug']:
    Talisman(app.server, content_security_policy=None)

# Make a list of all of the U.S. locations
us_locations = list(us_state_abbrev.keys()) + \
        ['Other Counties, WA', 'King and Snohomish Counties (excluding Life Care Center),\
         WA','United States of America', 'Life Care Center, Kirkland, WA']
us_locations.sort()
# Move 'United States of America' to the front
us_locations.insert(0, us_locations.pop(us_locations.index('United States of America')))

non_us_locations = list(set(unique_location_names()) - set(us_locations))
non_us_locations.sort()

# combine the two lists and make sure we don't somehow have duplicates while keeping the order we created
all_locations = us_locations + non_us_locations
all_locations = list(dict.fromkeys(all_locations))

# Get list of all sequential color themes
excluded_colorscales = ['plotly3','gray','haline','ice','solar','thermal']
named_colorscales = [s for s in px.colors.named_colorscales() if s not in excluded_colorscales]
style_lists = [[style,getattr(px.colors.sequential,style)] for style in dir(px.colors.sequential) if style.lower() in named_colorscales and len(getattr(px.colors.sequential,style)) >= 12]

# get minimum model date
min_date = min_model_date()


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script>
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
        ga('create', 'UA-164558144-1', 'auto');
        ga('send', 'pageview');
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

collapse_plot_options = html.Div(
    [
        dbc.Button(
        "Advanced Plot Options",
        id="collapse-button",
        className="mb-3",
        color="dark",
        outline=True,
        size="sm",
        block=True
        ),
        dbc.Collapse(
            [
                dbc.FormGroup(
                    [
                        dbc.Checklist(
                            options=[
                                {"label": "Semi-log Plot", "value": False}
                            ],
                            value=False, #HACK: notice that this is a boolean
                            id="log-scale-toggle",
                            switch=True,
                        ),
                        dbc.Tooltip(
                            "Plot y-axis using a logarithmic scale (Default: False)",
                            target="log-scale-toggle",
                            placement='right',
                            offset=0,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Checklist(
                            options=[
                                {"label": "Plot Actual Deaths and Cases", "value": True}
                            ],
                            value=[True], #HACK: Notice that this is a list
                            id="actual-values-toggle",
                            switch=True,
                        ),
                        dbc.Tooltip(
                            "For metrics with actual historical data (e.g.deaths/confirmed cases), plot actual values as bars and projected values as lines (Default: True)",
                            target="actual-values-toggle",
                            placement='right',
                            offset=0,
                        ),
                    ]
                ),
                dbc.FormGroup( #TODO: Fix Top and Left margins to align 
                    [
                        dbc.Label("IHME Colorscale"),
                        dbc.Col(
                            dcc.Dropdown(
                                id="ihme-color-dropdown",
                                options=[
                                    # TODO could we maybe add color swatches for the color scales?
                                    # Doesn't seem possible with dbc Dropdown because labels can only be strings
                                    {'label' : row[ 0 ], 'value' : row[ 0 ]} for row in style_lists
                                ],
                                value = "tempo"
                            ),
                        ),
                    ],
                ),
                dbc.FormGroup( #TODO: Fix Top and Left margins to align 
                    [
                        dbc.Label("LANL Colorscale"),
                        dbc.Col(
                            dcc.Dropdown(
                                id="lanl-color-dropdown",
                                options=[
                                    # TODO could we maybe add color swatches for the color scales?
                                    # Doesn't seem possible with dbc Dropdown because labels can only be strings
                                    {'label' : row[ 0 ], 'value' : row[ 0 ]} for row in style_lists
                                ],
                                value = "amp"
                            ),
                        ),
                    ],
                ),
            ],
            id="collapse-plot-options"
            )
        ]
    )

#controls - adapted from https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/
controls = dbc.Card(
    [
        html.H5("Filters", className="card-title"),
        dbc.FormGroup(
            [
                dbc.Label("Model"),
                dcc.Dropdown(
                    id="model-dropdown",
                    options=[
                        {"label": col, "value": col} for col in ['IHME','LANL']
                    ],
                    value=['IHME','LANL'],
                    multi=True
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Location"),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[
                        {"label": col, "value": col} for col in all_locations
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
                    options=metric_labels(),
                    value="deaths_mean",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Model Date", id='model-date-label'),
                dcc.DatePickerRange(
                    id='model-date-picker',
                    min_date_allowed=min_date,
                    max_date_allowed=datetime.today(),
                    start_date=datetime.today() - timedelta(days=30), #HACK: Temporarily fixes the colorscale issue for >12 models
                    end_date=datetime.today(),
                    initial_visible_month=datetime.today(),
                ),
                dbc.Tooltip(
                    f"Forecast generated in this date range",
                    target="model-date-label",
                    placement='right',
                    offset=0,
                ),
            ]
        ),
        collapse_plot_options
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(brand=title, color="primary", dark=True),
        html.Div(more_info_alert),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=3),
                dbc.Col(dcc.Graph(id="primary-graph", config=plotly_config), md=9),
            ],
            align="center",
        ),
        html.Hr(),
        dbc.Row(id='stat-cards'),
        html.Hr(),

        dbc.Navbar(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                dbc.Row(
                                    [
                                        dbc.Col(html.I(className="fa fa-twitter", style={"font-size":"32px"})),
                                        dbc.Col(dbc.NavbarBrand("Twitter", className="ml-2")),
                                    ],
                                    align="center",
                                    no_gutters=True,
                                ),
                                href="https://twitter.com/CovidProjection",
                            ),
                            width="auto"
                        ),
                        dbc.Col(
                                html.A(
                                    dbc.Row(
                                        [
                                            dbc.Col(html.I(className="fa fa-github-square", style={"font-size":"32px"})),
                                            dbc.Col(dbc.NavbarBrand("Github", className="ml-2"))
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    href="https://github.com/yuorme/covid-projections",
                                ),
                            width="auto"
                            )
                        ,
                    ],
                    align="center"
                    )
            ],
            color="dark",
            dark=True,
        ),
    html.Div(id='graph_data', style={'display': 'none'})
    ],
    fluid=True,
)

@app.callback(
    Output("more-info-collapse", "is_open"),
    [Input("more-info-button", "n_clicks")],
    [State("more-info-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-plot-options", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse-plot-options", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


def build_cards(dff, metric, model):

    metric_name = column_translator[metric]

    #latest data
    latest_version = dff.model_date.max()
    #TODO: Maybe add cards for latest versions of LANL and IHME
    dff_latest = dff[(dff.model_date == latest_version)]
    proj_latest = dff_latest[metric].max()
    proj_latest_model = dff_latest['model_name'].unique()[0]+' - '+dff_latest['model_version'].unique()[0]

    #historical max and mins
    version_max = dff.groupby(['model_name','model_version'])[metric].max()
    proj_max = np.max(version_max)
    proj_min = np.min(version_max)
    #model labels
    proj_max_model = ' - '.join(version_max.index[np.argmax(version_max)])
    proj_min_model = ' - '.join(version_max.index[np.argmin(version_max)])
    
    
    cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5(f"Projected Peak - Latest", id='projected-latest-header', className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_latest)}', className='card-text'),
                    html.P(f'{proj_latest_model}', className='card-text'),
                ])
            ], color="info", outline=True),
            dbc.Tooltip(
                f"Projected peak value for {column_translator[metric]} for the most recent model included in the selection",
                target="projected-latest-header",
                placement='top',
                offset=0,
            ),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5(f"Projected Peak - Maximum", id='projected-max-header', className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_max)}', className='card-text'),
                    html.P(f'{proj_max_model}', className='card-text'),
                ])
            ], color="danger", outline=True),
            dbc.Tooltip(
                f"Projected peak value for {column_translator[metric]} for the model with the highest value included in the selection",
                target="projected-max-header",
                placement='top',
                offset=0,
            )
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5("Projected Peak - Minimum", id='projected-min-header', className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_min)}', className='card-text'),
                    html.P(f'{proj_min_model}', className='card-text'),
                ])
            ], color="success", outline=True),
            dbc.Tooltip(
                f"Projected peak value for {column_translator[metric]} for the model with the lowest value included in the selection",
                target="projected-min-header",
                placement='top',
                offset=0,
            )
        ]),
    ]

    return cards

@app.callback(
    Output('graph_data', 'children'),
    [
        Input("model-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("metric-dropdown", "value"),
        Input("model-date-picker", "start_date"),
        Input("model-date-picker", "end_date")
    ]
)
def get_data(model, location, metric, start_date, end_date):
    '''Query SQL table for data and store the data as a dictionary client-side'''
    dff = filter_df(model, location, metric, start_date, end_date)
    return dff.to_json(date_format='iso', orient='split')


@app.callback(
    [Output("primary-graph", "figure"), Output("stat-cards", "children")],
    [
        Input('graph_data', 'children'),
        Input("model-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("metric-dropdown", "value"),
        Input("model-date-picker", "start_date"),
        Input("model-date-picker", "end_date"),
        Input("log-scale-toggle", "value"),
        Input("actual-values-toggle", "value"),
        Input("ihme-color-dropdown", "value"),
        Input("lanl-color-dropdown", "value")
    ],

)
def make_primary_graph(existing_data, model, location, metric, start_date, end_date, log_scale, actual_values, color_scale_ihme, color_scale_lanl):
    '''Callback for the primary historical projections line chart
    '''
    # if we don't already have existing stored data, get the data from the table
    if existing_data is None:
        dff = filter_df(model, location, metric, start_date, end_date)
    else:
        dff = pd.read_json(existing_data, orient='split')
        dff= dff.astype(dict((k, table_dtypes[k]) for k in dff.columns if k in table_dtypes))

    cards = build_cards(dff, metric, model)

    model_title = ' & '.join(dff.model_name.unique())

    plot_title = f'{model_title} - {location} - {column_translator[metric]}'

    #different sequential colorscales for different models
    num_models_ihme = len(dff[dff.model_name == 'IHME'].model_version.unique())
    num_models_lanl = len(dff[dff.model_name == 'LANL'].model_version.unique())

    ihme_color_scale = getattr(px.colors.sequential, color_scale_ihme)
    ihme_color_scale = ihme_color_scale[len(ihme_color_scale)-num_models_ihme:]

    lanl_color_scale = getattr(px.colors.sequential, color_scale_lanl)
    lanl_color_scale = lanl_color_scale[len(lanl_color_scale)-num_models_lanl:]

    # Change y-axis scale depending on toggle value
    y_axis_type = ("log" if log_scale else "-")
    if y_axis_type == 'log':
        dff = dff[dff[metric] > 3] # prevent tiny log scale values from showing up

    if 'confirmed' in metric or 'dea' in metric and actual_values:
        if 'LANL' in dff.model_name.unique():
            act_dff = dff[dff.model_name == 'LANL']
            act_dff = act_dff[(act_dff.date <= act_dff.model_date) & (act_dff.model_date == act_dff.model_date.max())]
        else:
            act_dff = dff[(dff.date <= dff.model_date) & (dff.model_date == dff.model_date.max())]
        act_dff = act_dff.drop_duplicates(keep='first')


        fig = px.line(
            dff[dff.date > dff.model_date],
            x='date',
            y=metric,
            color='model_label',
            color_discrete_sequence=ihme_color_scale + lanl_color_scale,
            title=plot_title,
            labels=column_translator,
            hover_name='model_version',
            hover_data=['model_name'],
        )
        actual = px.bar(
            act_dff,
            x='date',
            y=metric,
            hover_name='date',
            color_discrete_sequence=['#696969']
        )
        fig.add_trace(actual.data[0])
    else:
        fig = px.line(
            dff,
            x='date',
            y=metric,
            color='model_label',
            color_discrete_sequence=ihme_color_scale + lanl_color_scale,
            title=plot_title,
            labels=column_translator,
            hover_name='model_version',
            hover_data=['model_name']
        )

    fig.layout.template = 'ggplot2'
    fig.update_layout(
        showlegend=True,
        annotations=[dict(
            x=0.01,
            y=0.98,
            xref="paper",
            yref="paper",
            text="@CovidProjection",
            showarrow=False,
        )],
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
        ],
        yaxis=dict(fixedrange=True), #fix y-axis for scrollZoom to work properly
        yaxis_type=y_axis_type
    )

    if y_axis_type == 'log':
        fig.update_layout(yaxis = {'dtick': 1})

    return fig, cards

if __name__ == "__main__":
    app.run_server(debug=app_config['debug'], port=5000)
