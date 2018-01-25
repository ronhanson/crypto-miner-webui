FROM python:3.6

MAINTAINER Ronan Delacroix "ronan.delacroix@gmail.com"

COPY . /opt/app
WORKDIR /opt/app

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/opt/app

EXPOSE 5050
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5050", "--access-logfile", "-", "--error-logfile", "-"]

CMD ["kontron_crypto_miner_webui:app"]