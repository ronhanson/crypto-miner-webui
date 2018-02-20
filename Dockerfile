FROM python:3.6

MAINTAINER Ronan Delacroix "ronan.delacroix@gmail.com"

EXPOSE 5050

WORKDIR /opt/app

RUN pip3 install --upgrade pip

RUN pip3 install --no-cache-dir "flask>=0.10" arrow prometheus_client whitenoise gunicorn requests dpath kubernetes

ENV PYTHONPATH=$PYTHONPATH:/opt/app

COPY requirements.txt /opt/app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /opt/app

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5050", "--access-logfile", "-", "--error-logfile", "-"]

CMD ["crypto_miner_webui.web:app"]