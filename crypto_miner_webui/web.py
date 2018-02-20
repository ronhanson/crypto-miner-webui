#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2018 Ronan Delacroix
Crypto Mining Web UI
:author: Ronan Delacroix
"""
import os
import sys
from flask import Flask, render_template
from whitenoise import WhiteNoise
from . import metrics


# Flask setup
app = Flask('crypto-mining-webui',
            root_path=os.path.split(os.path.realpath(__file__))[0],
            template_folder='templates')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app_name = "Crypto Mining Web UI"


# Prometheus metrics setup
metrics.setup_metrics(app)


# Routes
@app.route('/')
def index():
    """
    Main index page
    """
    wallet_id = os.environ.get("WALLET_ID", None)
    if not wallet_id:
        raise Exception("ENV Variable WALLET_ID not set")

    wallet_api_url = os.environ.get("WALLET_API_URL", None)
    if not wallet_api_url:
        print('Warning - ENV Variable WALLET_API_URL not set, using "https://etn.spacepools.org/api/stats_address" by default.')
        wallet_api_url = 'https://etn.spacepools.org/api/stats_address'

    tmpl_dict = {
        'app_name': app_name,
        "wallet_id": wallet_id,
        "wallet_api_url": wallet_api_url,
        "grafana_host": os.environ.get("GRAFANA_SERVICE_HOST", None),
        "grafana_port": os.environ.get("GRAFANA_SERVICE_PORT", 80),
        "grafana_graph_id": os.environ.get("GRAFANA_GRAPH_ID", None)
    }
    return render_template('index.html', **tmpl_dict)

