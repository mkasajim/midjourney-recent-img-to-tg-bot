FROM debian:latest


RUN apt update && apt upgrade -y

RUN apt install git curl python3-pip ffmpeg -y

RUN pip3 install -U pip

RUN cd /

RUN git clone https://github.com/mkasajim/midjourney-recent-img-to-tg-bot

RUN cd midjourney-recent-img-to-tg-bot

WORKDIR /midjourney-recent-img-to-tg-bot

RUN pip3 install -r requirements.txt

CMD python3 main.py
