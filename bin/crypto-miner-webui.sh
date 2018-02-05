#!/bin/bash

gunicorn -b 0.0.0.0:5050 --access-logfile - --error-logfile - crypto_miner_webui:app