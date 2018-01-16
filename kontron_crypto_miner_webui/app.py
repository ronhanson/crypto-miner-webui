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
    wallet_values = requests.get("https://api.electromine.fr/stats_address?address="+electromine_wallet_address).json()

    wallet_stats = wallet_values.get('stats', {})

    wallet_payments = wallet_values.get('payments', [])

    payments = OrderedDict()
    for i in range(0, len(wallet_payments), 2):
        payment = wallet_payments[i].split(':')
        date_payment = arrow.get(wallet_payments[i+1])
        payments[payment[0]] = {
            'time': date_payment,
            'hash': payment[0],
            'amount': float(payment[1])/100.0,
            'fee': float(payment[2])/100.0,
            'mixin': payment[3],
            #'recipients': payment.get(4, '')
        }
    tmpl_dict = {
        'app_name': app_name,
        "wallet": tbx.text._dict_to_html_recurse(wallet_values, 2),
        "stats": wallet_stats,
        "wallet_address": electromine_wallet_address
    }
    return render_template('index.html', **tmpl_dict)

