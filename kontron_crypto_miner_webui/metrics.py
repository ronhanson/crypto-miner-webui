#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2018 Ronan Delacroix
Kontron Crypto Mining Web UI
:author: Ronan Delacroix
"""
from flask import Flask, request, Response
import time
import prometheus_client


# Prometheus
REQUEST_COUNT = prometheus_client.Counter(
    'request_count', 'App Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = prometheus_client.Histogram(
    'request_latency_seconds', 'Request latency',
    ['method', 'endpoint']
)


def before_request():
    request.start_time = time.time()


def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(request_latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

    return response


def setup_metrics(app):
    app.before_request(before_request)
    app.after_request(after_request)

    @app.route('/metrics')
    def metrics():
        return Response(prometheus_client.generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')




