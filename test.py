import asyncio
import aiohttp

from binance_api import BinanceAPI
from config import config

test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))
cle = test.get_listenkey()['listenKey']
print(cle)

session = aiohttp.ClientSession()  # handles the context manager


class EchoWebsocket:

    async def connect(self):
        self.websocket = await session.ws_connect(f"wss://stream.binance.com:9443/stream?streams={cle}")

    async def send(self, message):
        self.websocket.send_str(message)

    async def receive(self):
        result = (await self.websocket.receive())
        return result.data


async def main():
    echo = EchoWebsocket()
    await echo.connect()
    print(await echo.receive())  # "Hello World!"


if __name__ == '__main__':
    # The main loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())