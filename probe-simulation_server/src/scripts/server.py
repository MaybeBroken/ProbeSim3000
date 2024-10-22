import asyncio
import websockets
import time as t
import json
import socket

cliDead = False
sendRespawn = False
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

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


async def _buildServe():
    global hostname, IPAddr
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    async with websockets.serve(_echo, IPAddr, 8765):
        print(
            f"*********\n:SERVER(notice): listening on url: [{IPAddr}:8765]\n*********"
        )
        await asyncio.Future()


def startServer():
    asyncio.run(_buildServe())
