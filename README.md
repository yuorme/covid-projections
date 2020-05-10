<h2 align="center">
  COVID Projections Tracker
</h2>

<blockquote align="center">
Collecting and visualizing current and historical COVID-19 forecast data
</blockquote>

<p align="center">
  <a href="https://www.covid-projections.com/">
    🌐 covid-projections.com
  </a>
</p>

![COVID Projections Demo](assets/ihme_tracker_v1.gif)

[![Gitter](https://badges.gitter.im/covid-projections-tracker/community.svg)](https://gitter.im/covid-projections-tracker/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/yuorme/covid-projections) ![GitHub contributors](https://img.shields.io/github/contributors/yuorme/covid-projections) ![Website](https://img.shields.io/website?url=https%3A%2F%2Fwww.covid-projections.com)

<h3 id="overview" align="center">
👀 Overview
</h3>

Covid Projections Tracker is a tool that allows experts to easily track projection accuracy as well as changes in projections over time. Projectons may change as new data is incorporated or when model parameters or frameworks are updated. Covid Projections is under active development, current features are shown here.

#### Interactive Dashboard:
- Historical model projections for a given country or region (currently supports IHME and LANL data)
- Toggle between linear and semi-log plots
- Select models with forecast dates within a given date range

#### Data Scraper:
Displaying a model on our website is not an endorsement of model accuracy. We currently display historical trends for IHME and LANL models primarily because they were the first groups to make their data easily accessible.

- [IHME](http://www.healthdata.org/covid/data-downloads) - Non-linear mixed effects curve-fitting.
- [LANL](https://covid-19.bsvgateway.org/#link%20to%20forecasting%20site) - Statistical dynamical growth model accounting for population susceptibility.

<h3 id="developers_guide" align="center">
🖥️ Quick Start
</h3>

Covid Projections Tracker is built in Python 3.8.2 :snake:. The dashboard uses [Dash](https://github.com/plotly/dash) and [Plotly](https://github.com/plotly/plotly.py) to generate a Flask/React.js web application. The scraper is built using requests and BeautifulSoup with pandas for data manipulation.

#### Install Packages
Clone the repo and use pip or conda to install required packages:

`pip install requirements.txt`

#### Run Scraper
Data should be included but the scraper can be run using:

`python projections-scraper.py`

#### Run Dashboard
To run locally, you'll need to set debug mode to True in `config.py`. This prevents HTTPS protocol from being enforced. Then run ```python app.py``` and then point your browser to `127.0.0.1:5000`



