FROM python:3.6-jessie

MAINTAINER Ronan Delacroix "ronan.delacroix@gmail.com"

#RUN apt-get -y update && apt-get -y install python3 python3-pip

COPY . /opt/app
WORKDIR /opt/app

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/opt/app:/opt/current_folder

EXPOSE 5050
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5050", "--access-logfile", "-", "--error-logfile", "-"]

CMD ["kontron_crypto_miner_webui:app"]