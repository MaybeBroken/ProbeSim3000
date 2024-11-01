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
portNum = 8766

hostname = socket.gethostname()

serveIPAddr = socket.gethostbyname(hostname)
serveIp = f"ws://{serveIPAddr}:{portNum}"


async def _send_recieve(data):
    global var1, var2, serverDeath
    async with websockets.connect(serveIp) as websocket:
        if data == "!!#admin":
            await websocket.send("!!#admin")
            msg = js.decoder.JSONDecoder().decode(await websocket.recv())
            print(msg)


def runClient(data):
    try:
        asyncio.run(_send_recieve(data))
    except:
        for i in range(5):
            try:
                asyncio.run(_send_recieve(data))
                break
            except:
                ...


while True:
    runClient("!!#admin")
    t.sleep(2)
