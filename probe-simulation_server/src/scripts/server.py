import asyncio
import websockets
import time as t
import socket
import json

cliDead = False
cliKill = False
sendRespawn = False
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
cliConnected = False
droneCount = " -- "
nodePositions = []


def packList():
    return {
        "cliKill": cliKill,
        "cliDead": cliDead,
        "sendRespawn": sendRespawn,
    }


async def _echo(websocket):
    global cliConnected
    cliConnected = True
    while True:
        try:
            global cliDead, sendRespawn, cliKill, droneCount, nodePositions
            msg = json.decoder.JSONDecoder().decode(await websocket.recv())
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
        except websockets.ConnectionClosedError:
            cliConnected = False
            break
        except websockets.ConnectionClosedOK:
            cliConnected = False
            break
        except websockets.ConnectionClosed:
            cliConnected = False
            break


async def _buildServe(port):
    global hostname, IPAddr
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    async with websockets.serve(_echo, IPAddr, port):
        print(
            f"*********\n:SERVER(notice): listening on url: [{IPAddr}:{port}]\n*********"
        )
        await asyncio.Future()


def startServer(port):
    while True:
        asyncio.run(_buildServe(port))
