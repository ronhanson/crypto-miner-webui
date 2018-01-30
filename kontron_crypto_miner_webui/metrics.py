#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2018 Ronan Delacroix
Kontron Crypto Mining Web UI
:author: Ronan Delacroix
"""
import os
from flask import Flask, request, Response
import time
import prometheus_client
from kubernetes import client, config
import dpath
from . import b2h


# Prometheus
REQUEST_COUNT = prometheus_client.Counter(
    'request_count', 'App Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = prometheus_client.Histogram(
    'request_latency_seconds', 'Request latency',
    ['method', 'endpoint']
)


def convert_to_milli(val):
    """
    Converts a string to milli value in int.
    Useful to convert milli values from k8s.
    Examples:
        convert_to_milli('10m') -> 10
        convert_to_milli('10000m') -> 10000
        convert_to_milli('1') -> 1000
        convert_to_milli('100') -> 100000
    """
    if val[-1] == 'm':
        return int(val.rstrip('m'))
    else:
        return 1000 * int(val)


def get_k8s_metrics():
    """
    Retrieves dataset of cpu and memory metrics about pods and nodes from kubernetes API
    """
    if os.environ.get("LOAD_INCLUSTER_CONFIG", False):
        config.load_incluster_config()
    else:
        config.load_kube_config()
    v1 = client.CoreV1Api()

    # Nodes
    api_nodes = v1.list_node(watch=False)
    nodes = [p.to_dict() for p in api_nodes.items]

    cpu_capacities = dpath.util.values(nodes, '*/status/capacity/cpu')
    mem_capacities = dpath.util.values(nodes, '*/status/capacity/memory')
    pod_capacities = dpath.util.values(nodes, '*/status/capacity/pods')
    cpu_allocatables = dpath.util.values(nodes, '*/status/allocatable/cpu')
    mem_allocatables = dpath.util.values(nodes, '*/status/allocatable/memory')
    pod_allocatables = dpath.util.values(nodes, '*/status/allocatable/pods')

    cpu_capacity_total = sum([convert_to_milli(c) for c in cpu_capacities])
    mem_capacity_total = sum([b2h.human2bytes(c)/1024.0 for c in mem_capacities])
    pod_capacity_total = sum([int(c) for c in pod_capacities])
    cpu_allocatable_total = sum([convert_to_milli(c) for c in cpu_allocatables])
    mem_allocatable_total = sum([b2h.human2bytes(c)/1024.0 for c in mem_allocatables])
    pod_allocatable_total = sum([int(c) for c in pod_allocatables])

    # Pods
    exclude_namespaces = os.environ.get('EXCLUDE_POD_NAMESPACES', [])
    if exclude_namespaces:
        exclude_namespaces = exclude_namespaces.split(";")

    api_pods = v1.list_pod_for_all_namespaces(watch=False)
    pods = [p.to_dict() for p in api_pods.items if p.metadata.namespace not in exclude_namespaces]

    memory_requests = dpath.util.values(pods, '*/spec/containers/*/resources/requests/memory')
    cpu_requests = dpath.util.values(pods, '*/spec/containers/*/resources/requests/cpu')

    cpu_requests_total = sum([convert_to_milli(f) for f in cpu_requests])
    mem_requests_total = sum([b2h.human2bytes(f)/1024.0 for f in memory_requests])

    # Difference
    cpu_capacity_remaining = (cpu_allocatable_total - cpu_requests_total)
    mem_capacity_remaining = (mem_allocatable_total - mem_requests_total)

    return {
        # nodes
        "cpu_capacity": cpu_capacity_total,
        "mem_capacity": mem_capacity_total,
        "pod_capacity": pod_capacity_total,
        "cpu_allocatable": cpu_allocatable_total,
        "mem_allocatable": mem_allocatable_total,
        "pod_allocatable": pod_allocatable_total,
        # pods
        "cpu_requests": cpu_requests_total,
        "mem_requests": mem_requests_total,
        # diff
        "cpu_capacity_remaining": cpu_capacity_remaining,
        "mem_capacity_remaining": mem_capacity_remaining
    }


# K8s metrics caching
PROMETHEUS_METRICS = get_k8s_metrics()


def setup_gauge(key, label):
    """
    Helper method to setup a prometheus gauge
    """
    global PROMETHEUS_METRICS
    g = prometheus_client.Gauge(key, label)
    g.set_function(lambda: PROMETHEUS_METRICS[key])

# setup metrics once
setup_gauge('cpu_capacity', 'CPU Total Capacity (milli)')
setup_gauge('mem_capacity', 'Memory Total Capacity (Ki)')
setup_gauge('pod_capacity', 'Pod Total Capacity')
setup_gauge('cpu_allocatable', 'CPU Total Allocatable (milli)')
setup_gauge('mem_allocatable', 'Memory Total Allocatable (Ki)')
setup_gauge('pod_allocatable', 'Pod Total Allocatable')
setup_gauge('cpu_requests', 'CPU Requests Total (milli)')
setup_gauge('mem_requests', 'Memory Requests Total (Ki)')
setup_gauge('cpu_capacity_remaining', "CPU Remaining Capacity (milli)")
setup_gauge('mem_capacity_remaining', "Memory Remaining Capacity (Ki)")


#
def before_request():
    """
    HTTP Request timings helper
    """
    request.start_time = time.time()


def after_request(response):
    """
    HTTP Request timings, setting prometheus metric value
    """
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(request_latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response


def setup_metrics(app):
    """
    Setup Flask app with prometheus metrics
    """
    app.before_request(before_request)
    app.after_request(after_request)

    @app.route('/metrics')
    def metrics():
        # update k8s metrics each time this url is called.
        global PROMETHEUS_METRICS
        PROMETHEUS_METRICS = get_k8s_metrics()
        return Response(prometheus_client.generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')




