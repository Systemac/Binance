FROM python:3.8
COPY requirements.txt ./app/
COPY binance_api.py ./app/
COPY websocket_api.py ./app/
COPY main.py ./app/
COPY requirements.txt ./app/
VOLUME /etc/localtime:/etc/localtime:ro
VOLUME /your-config:/app/
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt-get update && apt-get install ntp -y
RUN sed 's/pool /#pool /g' /etc/ntp.conf > /tmp/ntp.conf.tmp
RUN echo "server 0.europe.pool.ntp.org" >> /tmp/ntp.conf.tmp
RUN echo "server 1.europe.pool.ntp.org" >> /tmp/ntp.conf.tmp
RUN echo "server 2.europe.pool.ntp.org" >> /tmp/ntp.conf.tmp
RUN echo "server 3.europe.pool.ntp.org" >> /tmp/ntp.conf.tmp
RUN mv /tmp/ntp.conf.tmp /etc/ntp.conf
RUN ntpd -qxg
RUN /etc/init.d/ntp start
VOLUME /etc/localtime:/etc/localtime:ro

CMD [ "python", "/app/main.py" ]