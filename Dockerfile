FROM ubuntu
RUN apt-get install software-properties-common
RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get update
RUN apt-get install ffmpeg gstreamer0.10-ffmpeg