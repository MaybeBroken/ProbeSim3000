from os import system as _system
import time as t
import asyncio
import socket
from direct.stdpy.threading import Thread
from mss import mss
from PIL import Image

try:
    import websockets
except:
    _system(f"python3 -m pip install websockets")

try:
    import json as js
except:
    _system(f"python3 -m pip install json")

cliDead = False
cliRespawn = False
devMode = True
serverDeath = False

hostname = socket.gethostname()
serveIPAddr = socket.gethostbyname(hostname)
serveIp = f"ws://{serveIPAddr}"


def packList(mainClass):
    return {
        "cliKill": serverDeath,
        "cliDead": cliDead,
        "sendRespawn": cliRespawn,
        "droneCount": mainClass.currentDroneCount,
        "nodePositions": mainClass.nodePositions,
    }


async def testServerConnection():
    async with websockets.connect(f"{serveIp}:8765") as websocket:
        await websocket.send("None")
        await websocket.close()
    async with websockets.connect(f"{serveIp}:8766") as websocket:
        await websocket.send("None")
        await websocket.close()


async def _send_recieve(mainClass, clientType):
    global serverDeath, cliDead, cliRespawn

    if clientType == "client":
        async with websockets.connect(f"{serveIp}:8765") as websocket:
            running = True
            while running:
                try:
                    await websocket.send(
                        js.encoder.JSONEncoder().encode(packList(mainClass=mainClass))
                    )
                    msg = js.decoder.JSONDecoder().decode(await websocket.recv())
                    if msg["cliKill"]:
                        serverDeath = True
                    else:
                        serverDeath = False
                    if msg["sendRespawn"]:
                        cliRespawn = True
                    else:
                        cliRespawn = False
                except websockets.exceptions.ConnectionClosedError:
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    break
                t.sleep(0.01)
    elif clientType == "stream":
        async with websockets.connect(f"{serveIp}:8766") as websocket:
            running = True
            while running:
                sct = mss()
                sct.with_cursor = True
                bounding_box = {
                    "top": 0,
                    "left": 0,
                    "width": 1920,
                    "height": 1080,
                }
                img = sct.grab(bounding_box)
                img = Image.frombytes("RGB", (img.width, img.height), img.rgb)
                img = img.resize((int(640 / 4), int(360 / 4)))
                img_bytes = img.tobytes()
                await websocket.send(img_bytes)
                t.sleep(0.01)


def runClient(mainClass, clientType):
    asyncio.run(
        _send_recieve(mainClass=mainClass, clientType=clientType),
    )
