#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_talisman import Talisman

import plotly.graph_objects as go
import plotly.express as px

from region_abbreviations import us_state_abbrev
from column_translater import column_translator


#load data
def load_projections():

    df = pd.read_csv(os.path.join('data','merged_projections.csv'), nrows=50)
    
    dtypes = [
        'category','str',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'category','category',
        'float32','float32','float32',
        'float32','float32','float32',
    ]

    pd_dtypes = dict(zip(df.columns, dtypes))

    df = pd.read_csv(os.path.join('data','merged_projections.csv'), dtype=pd_dtypes)
    df = df[df.model_version != '2020_04_05.05.us']

    df['date'] = pd.to_datetime(df['date'])
    df['model_date'] = pd.to_datetime(df['model_version'].str[0:10].str.replace('_','-'))
    df['location_abbr'] = df['location_name'].map(us_state_abbrev)

    print('final mem usage:', df.info(memory_usage='deep'))

    return df

def filter_df(df, model, location, metric, start_date, end_date):

    dff = df.copy()

    dff = dff[
        (dff.location_name == location) & 
        (dff.model_name.isin(model)) &
        (dff.model_date >= start_date) &
        (dff.model_date <= end_date) & 
        (dff.date > '2020-02-15') &
        (dff.date < '2020-07-15')
        ]

    dff.dropna(subset=[metric], inplace=True)

    dff['model_label'] = dff['model_name'].astype('str') + '-' + dff['model_date'].dt.strftime("%m/%d").str[1:]

    return dff

df = load_projections()

# Make a list of all of the U.S. locations
us_locations = list(us_state_abbrev.keys()) + \
        ['Other Counties, WA', 'King and Snohomish Counties (excluding Life Care Center),\
         WA','United States of America', 'Life Care Center, Kirkland, WA']
us_locations.sort()
# Move 'United States of America' to the front
us_locations.insert(0, us_locations.pop(us_locations.index('United States of America')))

non_us_locations = list( set(df.location_name.unique()) - set(us_locations))
non_us_locations.sort()

# combine the two lists and make sure we don't somehow have duplicates while keeping the order we created
all_locations = us_locations + non_us_locations
all_locations = list(dict.fromkeys(all_locations))

# Get list of all sequential color themes
excluded_colorscales = ['plotly3','gray','haline','ice','solar','thermal']
named_colorscales = [s for s in px.colors.named_colorscales() if s not in excluded_colorscales]
style_lists = [[style,getattr(px.colors.sequential,style)] for style in dir(px.colors.sequential) if style.lower() in named_colorscales and len(getattr(px.colors.sequential,style)) >= 12]

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
Talisman(app.server, content_security_policy=None)


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
                                        {"label": "Semi-log Plot", "value": [False, True]}
                                    ],
                                    value=False,
                                    id="log-scale-toggle",
                                    switch=True,
                                ),
                            ]
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Checklist(
                                    options=[
                                        {"label": "Plot Actual Deaths and Cases", "value": [False, True]}
                                    ],
                                    value=True, #BUG: Doesn't default to display selected on app intialization
                                    id="actual-values-toggle",
                                    switch=True,
                                ),
                            ]
                        ),
                        dbc.FormGroup( #TODO: Fix Top and Left margins to align 
                            [
                                dbc.Label("IHME Color"),
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
                                dbc.Label("LANL Color"),
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
                    options=[
                        {"label": column_translator[col], "value": col} for col in df.select_dtypes(include=np.number).columns.sort_values().tolist() #TODO: Might be nice if metrics were sorted alphabetically by label rather than column names
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
                    start_date=df.model_date.min() + timedelta(days=2), #HACK: Temporarily fixes the colorscale issue for >12 models
                    end_date=datetime.today(),
                    initial_visible_month=datetime.today(),
                ),
            ]
        ),
        collapse_plot_options
    ],
    body=True,
)

plotly_config = dict(
    scrollZoom = True,
    displaylogo= False,
    showLink = False,
    toImageButtonOptions={
        'format':'png',
        'filename':'covid-projections',
        #twitter optimized 16:9 size
        'width':1200,
        'height':675
    },
    modeBarButtonsToRemove = [
        'sendDataToCloud',
        'zoomIn2d',
        'zoomOut2d',
        'hoverClosestCartesian',
        'hoverCompareCartesian',
        'hoverClosest3d',
        'hoverClosestGeo',
        'resetScale2d'
    ],
)

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(brand=title, color="primary", dark=True),
        html.Div(dbc.Alert("Historical model projections for a given country or region (currently supports IHME and LANL projections)", color="primary", id='alert')),
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
        )
    ],
    fluid=True,
)

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
                dbc.CardHeader([html.H5(f"Projected Peak - Latest", className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_latest)}', className='card-text'),
                    html.P(f'{proj_latest_model}', className='card-text'),
                ])
            ], color="info", outline=True)
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5(f"Projected Peak - Maximum", className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_max)}', className='card-text'),
                    html.P(f'{proj_max_model}', className='card-text'),
                ])
            ], color="danger", outline=True)
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5("Projected Peak - Minimum", className="card-text")]), #TODO:add dbc.Tooltip to explain what this card means
                dbc.CardBody([
                    html.H2(f'{int(proj_min)}', className='card-text'),
                    html.P(f'{proj_min_model}', className='card-text'),
                ])
            ], color="success", outline=True)
        ]),
    ]

    return cards

@app.callback(
    Output("stat-cards", "children"),
    [
        Input("model-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("metric-dropdown", "value"),
        Input("model-date-picker", "start_date"),
        Input("model-date-picker", "end_date")
    ],
)
def make_stat_cards(model, location, metric, start_date, end_date):
    '''Callback for the historical projections stats cards
    '''
    dff = filter_df(df, model, location, metric, start_date, end_date)

    return build_cards(dff, metric, model)

@app.callback(
    Output("primary-graph", "figure"),
    [
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
def make_primary_graph(model, location, metric, start_date, end_date, log_scale, actual_values, color_scale_ihme, color_scale_lanl):
    '''Callback for the primary historical projections line chart
    '''
    dff = filter_df(df, model, location, metric, start_date, end_date)
    
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
        dff = dff[dff[metric] > 3] #prevent tiny log scale values from showing up


    if 'confirmed' in metric or 'dea' in metric and actual_values:
        fig = px.line(
            dff[dff.date > dff.model_date],
            x='date',
            y=metric,
            color='model_label',
            color_discrete_sequence=ihme_color_scale + lanl_color_scale,
            title=plot_title,
            labels=column_translator,
            hover_name='model_version',
            hover_data=['model_name']
        )
        actual = px.bar(
            dff[(dff.date <= dff.model_date) & (dff.model_date == dff.model_date.max())],
            x='date',
            y=metric,
            hover_name='model_version',
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

    return fig

if __name__ == "__main__":
    app.run_server(debug=False, port=5000)
