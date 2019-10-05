FROM ubuntu:18.04

MAINTAINER Romain Thierry-Laumont "romain.121@hotmail.fr"

# Python install
RUN apt-get update -y --no-install-recommends; \
    apt-get install -y wget python-setuptools python-pip vim htop nano; \
    apt-get clean; \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/Miniconda3.sh; \
    /bin/bash -b -p -f ~/Miniconda3.sh -b $HOME/Miniconda3

# Install pip in miniconda
RUN /root/miniconda3/bin/conda install pip && \
    /root/miniconda3/bin/pip install --upgrade pip && \
    /root/miniconda3/bin/pip install --upgrade setuptools

# installation of dependencies
RUN apt-get -y update && apt-get install -y unzip gfortran openssh-server


RUN mkdir Avalon
RUN mkdir Avalon/resources

COPY resources /Avalon/resources
COPY requirements.txt /Avalon
RUN /root/miniconda3/bin/pip install -r Avalon/requirements.txt
COPY app.py /Avalon
COPY pylib.py /Avalon

WORKDIR Avalon
CMD ["sh", "-c", "/root/miniconda3/bin/python app.py"]


#ENV WEBSERVICEHOST 0.0.0.0
#ENV WEBSERVICEPORT 5000
#ENV DBHOST rethinkdb
#ENV DBPORT 28015

# CMD ["sh", "-c", "/root/miniconda3/bin/python app/app.py ${WEBSERVICEHOST} ${WEBSERVICEPORT} ${DBHOST} ${DBPORT}"]
