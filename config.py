import os
from dotenv import load_dotenv
load_dotenv()

app_config = {
    'debug' : True, #Set flask debug mode: True for development, False for production
    'sqlalchemy_database_uri' : f'postgresql+psycopg2://postgres:{os.environ.get("COVID_PRED_POSTGRES_PASS")}@'\
                                    f'{os.environ.get("COVID_PRED_RDS_URL")}/covid_projections?sslmode=verify-ca'\
                                f'&sslrootcert=rds-ca-2019-root.pem',
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
