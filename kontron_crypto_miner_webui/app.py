#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2018 Ronan Delacroix
Kontron Crypto Mining Web UI
:author: Ronan Delacroix
"""
import os
from flask import Flask, request, Response, render_template, url_for
from functools import wraps
import json
from flask.views import MethodView
import logging
import arrow
import time
import traceback
from whitenoise import WhiteNoise
from datetime import datetime, timedelta
from . import metrics
import requests
import tbx.text
from collections import OrderedDict

# Flask
app = Flask('kontron-crypto-mining-webui',
            root_path=os.path.split(os.path.realpath(__file__))[0],
            template_folder='templates')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app_name = "Kontron Crypto Mining Web UI"

# Prometheus
metrics.setup_metrics(app)


# Routes
@app.route('/')
def index():
    electromine_wallet_address = os.environ.get("ELECROMINE_WALLET", None)
    if not electromine_wallet_address:
        raise Exception("ENV Variable ELECROMINE_WALLET not set")

    tmpl_dict = {
        'app_name': app_name,
        "wallet_address": electromine_wallet_address
    }
    return render_template('index.html', **tmpl_dict)

