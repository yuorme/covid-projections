app_config = {
    'debug' : False, #Set flask debug mode: True for development, False for production
    'sqlalchemy_database_uri' : 'postgresql+psycopg2://localhost/covid_projections',
    'database_name' : 'projections'
}

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
