import asyncio
import websockets
import time as t
import socket
from os import system

try:
    import json
except ImportError:
    system("python3 -m pip install json")
try:
    import functools
except ImportError:
    system("python3 -m pip install functools")
cliDead = False
cliKill = False
sendRespawn = False
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
cliConnected = False
droneCount = " -- "
nodePositions = {
    "drones": [tuple],
    "ship": tuple,
    "voyager": tuple,
}
cliDispBuffer = None


def packList():
    return {
        "cliKill": cliKill,
        "cliDead": cliDead,
        "sendRespawn": sendRespawn,
    }


async def _echo(websocket, serverType):
    global cliDead, sendRespawn, cliKill, droneCount, nodePositions, cliDispBuffer, cliConnected, cliDispBufferTotal
    if serverType == "dataServer":
        while True:
            try:
                data = await websocket.recv()
                try:
                    msg = json.decoder.JSONDecoder().decode(data)
                    cliConnected = True
                    if msg["cliDead"]:
                        cliDead = True
                    else:
                        cliDead = False
                        sendRespawn = False

                    nodePositions = msg["nodePositions"]
                    droneCount = msg["droneCount"]

                    await websocket.send(json.encoder.JSONEncoder().encode(packList()))
                    if cliKill:
                        cliKill = False
                except json.JSONDecodeError:
                    ...
            except websockets.ConnectionClosedError:
                cliConnected = False
                break
            except websockets.ConnectionClosedOK:
                cliConnected = False
                break
            except websockets.ConnectionClosed:
                cliConnected = False
                break


async def _buildServe(port, serverType: str):
    global hostname, IPAddr
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    async with websockets.serve(
        functools.partial(_echo, serverType=serverType),
        IPAddr,
        port,
    ):
        print(
            f"*********\n:{serverType.upper()} (notice): listening on url {IPAddr}:{port}\n*********\n"
        )
        await asyncio.Future()


def startServer(port, serverType):
    asyncio.run(_buildServe(port, serverType))
