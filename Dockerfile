FROM python:3.8

COPY requirements.txt ./
COPY binance_api.py ./
COPY websocket_api.py ./
COPY config.py ./
COPY main.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]