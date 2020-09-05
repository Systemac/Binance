FROM python:3.8
COPY requirements.txt binance_api.py websocket_api.py main.py requirements.txt ./app/
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD [ "python", "/app/main.py" ]