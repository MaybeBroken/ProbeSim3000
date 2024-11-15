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


def packList():
    return {
        "cliKill": cliKill,
        "cliDead": cliDead,
        "sendRespawn": sendRespawn,
    }


async def _echo(websocket):
    running = True
    while running:
        try:
            global cliDead, sendRespawn, cliKill
            msg = json.decoder.JSONDecoder().decode(await websocket.recv())
            if msg["cliDead"]:
                cliDead = True
                cliKill = False
            else:
                cliDead = False
                sendRespawn = False
                cliKill = False
            await websocket.send(json.encoder.JSONEncoder().encode(packList()))
            # if sendRespawn:
            #     sendRespawn = False
        except:
            ...


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
        try:
            asyncio.run(_buildServe(port))
        except:
            print("server err @ <Main.Thread.server -> 51>")
