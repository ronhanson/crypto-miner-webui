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
import traceback
from whitenoise import WhiteNoise
from datetime import datetime, timedelta


# Flask
app = Flask('kontron-crypto-mining-webui',
            #secret_key='MyVeryOwnSecretSaltKey',
            root_path=os.path.split(os.path.realpath(__file__))[0],
            template_folder='templates')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app_name = "Kontron Crypto Mining Web UI"


@app.route('/')
def index():
    tmpl_dict = {'app_name': app_name}
    return render_template('index.html', **tmpl_dict)
