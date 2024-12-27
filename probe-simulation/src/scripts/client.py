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

cliDead = False
cliRespawn = False
devMode = True
serverDeath = False

portNum = 8765
hostname = socket.gethostname()
serveIPAddr = socket.gethostbyname(hostname)
serveIp = f"ws://{serveIPAddr}:8765"


def packList(mainClass):
    return {
        "cliKill": serverDeath,
        "cliDead": cliDead,
        "sendRespawn": cliRespawn,
        "droneCount": mainClass.currentDroneCount,
        "nodePositions": mainClass.nodePositions,
    }


async def _send_recieve(mainClass):
    global serverDeath, cliDead, cliRespawn
    async with websockets.connect(serveIp) as websocket:
        running = True
        while running:
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


def runClient(mainClass):
    asyncio.run(_send_recieve(mainClass=mainClass))
