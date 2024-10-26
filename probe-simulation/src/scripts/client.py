from os import system as _system
import time as t
import asyncio
import socket

try:
    import websockets
except:
    _system(f"python3 -m pip install websockets")

try:
    import json as js
except:
    _system(f"python3 -m pip install json")

var1 = None
var2 = None
devMode = True
serverDeath = False

serverContents = []
portNum = 8765

hostname = socket.gethostname()

serveIPAddr = socket.gethostbyname(hostname)
serveIp = f"ws://{serveIPAddr}:8765"


async def _send_recieve(data):
    global var1, var2, serverDeath
    async with websockets.connect(serveIp) as websocket:
        encoder = js.encoder.JSONEncoder()
        if data == "!!#death":
            await websocket.send("!!#death")
            var1 = await websocket.recv()
        if data == "!!#update":
            await websocket.send("!!#update")
            msg = js.decoder.JSONDecoder().decode(await websocket.recv())
            if msg["cliKill"]:
                serverDeath = True
            else:
                serverDeath = False


def runClient(data):
    if data == "!!#update":
        asyncio.run(_send_recieve(data))
    else:
        try:
            asyncio.run(_send_recieve(data))
        except:
            for i in range(5):
                try:
                    asyncio.run(_send_recieve(data))
                    break
                except:
                    ...
