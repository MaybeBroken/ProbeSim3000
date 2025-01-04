from os import system as _system
import time as t
import asyncio
import socket
from direct.stdpy.threading import Thread

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


def runClient(mainClass, clientType):
    asyncio.run(
        _send_recieve(mainClass=mainClass, clientType=clientType),
    )
