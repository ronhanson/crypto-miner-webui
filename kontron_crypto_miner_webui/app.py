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
from . import b2h
import dpath

# Flask
app = Flask('kontron-crypto-mining-webui',
            root_path=os.path.split(os.path.realpath(__file__))[0],
            template_folder='templates')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app_name = "Kontron Crypto Mining Web UI"

# Prometheus
metrics.setup_metrics(app)


# Routes
@app.route('/test')
def test():
    from kubernetes import client, config
    config.load_kube_config()

    exclude_namespaces = os.environ.get('EXCLUDE_POD_NAMESPACES', [])
    if exclude_namespaces:
        exclude_namespaces = exclude_namespaces.split(";")

    v1 = client.CoreV1Api()
    api_pods = v1.list_pod_for_all_namespaces(watch=False)

    pods = [p.to_dict() for p in api_pods.items if p.metadata.namespace not in exclude_namespaces]

    memory_requests = dpath.util.values(pods, '*/spec/containers/*/resources/requests/memory')
    cpu_requests = dpath.util.values(pods, '*/spec/containers/*/resources/requests/cpu')

    total_cpu_requests = sum([int(f.replace('m', '')) for f in cpu_requests])
    total_memory_requests = sum([b2h.human2bytes(f)//1024 for f in memory_requests])

    html = "Total Memory %sMi / %sKi<br>Total CPU %sm<br><br>" % (total_memory_requests//1024, total_memory_requests, total_cpu_requests)

    total_cpu_lim = 0
    total_cpu_req = 0
    total_memory_lim = 0
    total_memory_req = 0

    html += "Listing pods with their IPs:<br>"
    for i in api_pods.items:
        html += "<br>&nbsp;&nbsp;%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)

        for container in i.spec.containers:
            html += "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&gt; %s" % (container.name)
            cpu_limits = 0
            cpu_requests = 0
            memory_limits = 0
            memory_requests = 0
            if container.resources.limits:
                lim = container.resources.limits
                cpu_limits = int(lim['cpu'].rstrip('m')) if 'cpu' in lim else 0
                memory_limits = b2h.human2bytes(lim['memory'])//1024 if 'memory' in lim else 0
            if container.resources.requests:
                req = container.resources.requests
                cpu_requests = int(req['cpu'].rstrip('m')) if 'cpu' in req else 0
                memory_requests = b2h.human2bytes(req['memory'])//1024 if 'memory' in req else 0

            total_cpu_lim += cpu_limits
            total_cpu_req += cpu_requests
            total_memory_lim += memory_limits
            total_memory_req += memory_requests
            html += "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cpu req : %d - cpu lim : %d - mem req : %d - mem lim : %d" % (cpu_requests, cpu_limits, memory_requests, memory_limits)
        html += "<br>"
    html += "<br>&nbsp;&nbsp;Totals &gt; total cpu req : %d - total cpu lim : %d - total mem req : %d - total mem lim : %d" % (total_cpu_req, total_cpu_lim, total_memory_req, total_memory_lim)
    return html


# Routes
@app.route('/test2')
def test2():
    return str(metrics.get_prometheus_metrics())


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

