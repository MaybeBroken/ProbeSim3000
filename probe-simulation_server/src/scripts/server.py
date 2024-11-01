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
    return {"cliKill": cliKill}


async def _echo(websocket):
    global cliDead, sendRespawn
    msg = await websocket.recv()
    if msg == "!!#death":
        cliDead = True
        while cliDead:
            if sendRespawn:
                await websocket.send("!!#respawn")
                sendRespawn = False
                cliDead = False
                break
            else:
                t.sleep(0.25)
    elif msg == "!!#update":
        await websocket.send(json.encoder.JSONEncoder().encode(packList()))
    elif msg == "!!#admin":
        await websocket.send(json.encoder.JSONEncoder().encode(packList()))


async def _buildServe(port):
    global hostname, IPAddr
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    async with websockets.serve(_echo, IPAddr, port):
        print(
            f"*********\n:SERVER(notice): listening on url: [{IPAddr}:8765]\n*********"
        )
        await asyncio.Future()


def startServer(port):
    while True:
        try:
            asyncio.run(_buildServe(port))
        except:
            print("cli err")
