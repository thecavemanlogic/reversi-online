import asyncio
import websockets

async def echo(ws, path):
    async for msg in ws:
        await ws.send(msg)

async def main():
    async with websockets.serve(echo, "0.0.0.0", 9090):
        await asyncio.Future()

asyncio.run(main())