FROM ubuntu:20.04 as base

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update ; \
  apt-get install -y wget \
    libx11-dev unzip sudo \
    xvfb x11vnc \
    software-properties-common


RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update --fix-missing
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip
RUN useradd -m eyesim
#COPY --chown=eyesim:eyesim . /home/eyesim

USER eyesim
WORKDIR /home/eyesim
# Install dependencies
COPY ./requirements.txt /home/eyesim/requirements.txt
RUN python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt
RUN wget https://roblab.org/eyesim/ftp/EyeSim-1.5.2-Linux.tar.gz
RUN wget https://roblab.org/eyesim/ftp/Eyesim-Examples.zip
RUN tar -xzf EyeSim-1.5.2-Linux.tar.gz && rm EyeSim-1.5.2-Linux.tar.gz && \
  unzip Eyesim-Examples.zip && rm Eyesim-Examples.zip

USER root
WORKDIR /home/eyesim
RUN cp -r ./eyesimX ./EyeSim && cd EyeSim && ./install.sh

USER eyesim