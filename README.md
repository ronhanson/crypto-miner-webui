Cluster Crypto Miner - Web UI & metrics
=======================================

***Project sponsored by [Kontron](https://www.kontron.com)***

***Project Lead and [related articles](https://medium.com/@samnco) by [Samuel Cozannet](https://www.linkedin.com/in/scozannet/)***

What is this ?
--------------

This small demo aims to provides a simple dummy web interface allowing to vizualize live data about crypto currency 
mining made on Kontron hardware, mining adaptative to hardware load (cpu).

This app has been made to run in a Kubernetes cluster, even if nothing abides you from running it somewhere else, 
no code change required. The /metrics url is related to Prometheus / Kubernetes.

On top of the dummy index page, this app provides prometheus metrics that allow for inverse CPU/Memory load calculation. 
Exposed metrics are useful if you want to use Kubernetes Horizontal Load Balancing to scale apps based on remaining CPU
capacity of the cluster.

This small project is not production grade and is only made for Mobile World Congress to demo.


Run
---

#### Python script usage (dev mode)

    bin/kontron-crypto-miner-webui <MY_ELECTROMINE_WALLET_KEY>


#### Run using gunicorn

First set required ENV variable (see below), then :

    gunicorn -b 0.0.0.0:5050 --access-logfile - --error-logfile - kontron_crypto_miner_webui:app

*or*

    bin/kontron-crypto-miner-webui.sh 


#### Docker Build and Run

    docker build . -t mwc-miner-metrics:latest

    docker run -p 5050:5050 -e ELECROMINE_WALLET=<MY_ELECTROMINE_WALLET_KEY> mwc-miner-metrics:latest

Finally go to [http://localhost:5050/](http://localhost:5050/)


Env variables
-------------

#### Index page related

  - ***ELECTROMINE_WALLET*** <required to display index page> - public wallet key to display wallet data on index page

#### Kubernetes / Prometheus Metrics related

  - ***EXCLUDE_POD_NAMESPACES*** <optional> - exlude pod namespaces from computed Prometheus CPU/Memory metrics.
  - ***LOAD_INCLUSTER_CONFIG*** <optional> - If set ('ON' or any value), the kubernetes config will be loaded from incluster
in opposition to default config load method (load_kube_config / load_incluster_config).


Compatibility
-------------

This client can be used on Linux, OSX systems, or Windows.

This libraries are compatibles with Python 2.7+ and Python 3.X.

Mainly tested on 2.7 and 3.6.


Author and Licence
----------------

Project url : https://github.com/ronhanson/python-kontron-crypto-miner-webui

Copyright © 2018 [Ronan Delacroix](www.linkedin.com/in/ronan-delacroix)

This program is released under MIT Licence. Feel free to use it or part of it anywhere you want.
 
