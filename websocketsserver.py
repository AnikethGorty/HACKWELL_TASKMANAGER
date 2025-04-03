import asyncio
import websockets
import json

async def handle_connection(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print(f"Received Task: {data}")
        await websocket.send(f"Task '{data['task_name']}' received successfully!")

start_server = websockets.serve(handle_connection, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
