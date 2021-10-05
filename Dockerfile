FROM python:3.9-slim

MAINTAINER Romain Thierry-Laumont "romain.121@hotmail.fr"

RUN apt-get update && apt-get -y upgrade && apt-get install -y ffmpeg

COPY pip.conf /etc/pip.conf
COPY avalon-api /avalon-api
RUN pip install -r avalon-api/requirements/requirements.txt
WORKDIR avalon-api
CMD ["sh", "-c", "python api.py"]


#ENV WEBSERVICEHOST 0.0.0.0
#ENV WEBSERVICEPORT 5000
#ENV DBHOST rethinkdb
#ENV DBPORT 28015

# CMD ["sh", "-c", "/root/miniconda3/bin/python app/app.py ${WEBSERVICEHOST} ${WEBSERVICEPORT} ${DBHOST} ${DBPORT}"]
