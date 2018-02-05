#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2018 Ronan Delacroix
Crypto Mining Web UI
:author: Ronan Delacroix
"""
import os
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
    electromine_wallet_address = os.environ.get("ELECTROMINE_WALLET", None)
    if not electromine_wallet_address:
        raise Exception("ENV Variable ELECTROMINE_WALLET not set")

    tmpl_dict = {
        'app_name': app_name,
        "wallet_address": electromine_wallet_address,
        "grafana_host": os.environ.get("GRAFANA_SERVICE_HOST", None),
        "grafana_port": os.environ.get("GRAFANA_SERVICE_PORT", 80),
        "grafana_graph_id": os.environ.get("GRAFANA_GRAPH_ID", None)
    }
    return render_template('index.html', **tmpl_dict)

