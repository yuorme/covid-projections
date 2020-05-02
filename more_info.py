import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

more_info_card = dbc.CardDeck(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Purpose", className="card-title"),
                    dcc.Markdown('''
                        Covid Projections Tracker is a tool that allows experts to easily track **projection accuracy** as well as **changes in projections over time**. 
                        Projectons may change as new data is incorporated or when model parameters or frameworks are updated. 
                        
                        COVID-19 is novel disease and there is a tremendous amount of uncertainty in all projections. 
                        Confidence intervals are available (selectable via the Metric dropdown) but are not overlayed for the sake of creating a cleaner visualization. 
                    ''',
                    className="card-text",
                    ),
                ]
            ),
            color='info',
            outline=True,
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Models", className="card-title"),
                    dcc.Markdown('''
                        Displaying a model on our website is **not an endorsement** of model accuracy. 
                        We currently display historical trends for IHME and LANL models primarily because they were the first groups to make their data easily accessible. 
                        
                        [**IHME**](https://covid19.healthdata.org/united-states-of-america) - Non-linear mixed effects curve-fitting. There are
                        [known](https://www.statnews.com/2020/04/17/influential-covid-19-model-uses-flawed-methods-shouldnt-guide-policies-critics-say/) 
                        [issues](https://twitter.com/CT_Bergstrom/status/1250304069119275009) with this model.
                        
                        [**LANL**](https://covid-19.bsvgateway.org/#link%20to%20forecasting%20site) - Statistical dynamical growth model accounting for population susceptibility. 
                        ''',
                        className="card-text",
                    ),
                ]
            ),
            color='info',
            outline=True,
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Other Resources", className="card-title"),
                    dcc.Markdown('''
                        Other great projection resources include:

                        [**CDC COVID-19 Site**](https://www.cdc.gov/coronavirus/2019-ncov/covid-data/forecasting-us.html) - 
                        Excellent resource that provides overview of how modeling works as well as current model projections from multiple sources. 
                        Uses forecasts compiled by the Reich lab at UMass Amherst.
                        
                        [**Reich Lab**](https://reichlab.io/covid19-forecast-hub/) - 
                        The most comprehensive public collection of projection data currently available (over 20 at time of writing).
                        Using collected data to build an ensemble projection model.

                        [**CovidCareMap**](https://www.covidcaremap.org/maps/ihme-explorer/#1.75/38/-46) - 
                        Choropleth map displaying current IHME projections over time.
                    ''',
                        className="card-text",
                    ),
                ]
            ),
            color='info',
            outline=True,
        ),
    ]
)

more_info_alert = dbc.Alert(
        children=[
            "Historical model projections for a given country or region (currently supports IHME and LANL projections) ", 
            dbc.Button('More Info', id='more-info-button', size='sm', outline=False, color='info', className='ml-1'),
            dbc.Collapse(
                children=[
                    html.Hr(),
                    more_info_card,
                ],
                id="more-info-collapse"
            ),
        ],
        color="primary", 
        id='alert'
)