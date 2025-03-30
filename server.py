#    Copyright 2025 AzureTecDevs
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import asyncio
import websockets
import json
import loglib as logging
import conf
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
import sys

# Terminal GUI output
class ConsolePopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("openServer Console")
        self.geometry("500x300")
        self.text_area = ScrolledText(self, wrap=tk.WORD, state='disabled')
        self.text_area.pack(expand=True, fill='both')
        self.protocol("WM_DELETE_WINDOW", self.hide)

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()

    def append_text(self, text):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')
        self.text_area.yview(tk.END)

class RedirectedConsole:
    def __init__(self, console_popup):
        self.console_popup = console_popup

    def write(self, message):
        if message.strip():
            self.console_popup.append_text(message)

    def flush(self):
        pass

def background_task(console_popup):
    asyncio.run(start_server(HOST, PORT))
    console_popup.append_text("Server stopped.")

# Global set to store connected clients
connected_clients = set()

async def handle_client(websocket):
    """
    Handles a new client connection.

    Args:
        websocket: The WebSocket object for the client.
    """
    client_address = websocket.remote_address
    logging.info(f"Client connected from {client_address}")
    connected_clients.add(websocket)  # Add the client to the set

    try:
        # Send a welcome message to the client
        welcome_message = conf.MOTD
        welcome_message['client_address'] = str(client_address)
        await websocket.send(json.dumps(welcome_message))

        # Stay connected and process messages from the client
        async for message in websocket:
            try:
                # Parse the message as JSON
                data = json.loads(message)
                message_type = data.get("type")

                if conf.SERVER_TYPE == 'chat':
                    payload = data.get("payload")
                    user = data.get("user")
                    if message_type == "chat":
                        # Broadcast the chat message to all other clients
                        sender_address = str(client_address)
                        await broadcast_message(payload, sender_address, 'chat', user)
                    elif message_type == "user_joined":
                        # Broadcast the chat message to all other clients
                        sender_address = str(client_address)
                        await broadcast_message(payload, sender_address, 'user_joined', user)
                    elif message_type == "user_left":
                        # Broadcast the chat message to all other clients
                        sender_address = str(client_address)
                        await broadcast_message(payload, sender_address, 'user_left', user)
                    elif message_type == "echo":
                        # Send the payload back to the sender
                        echo_response = {"type": "echo_response", "payload": payload, "sender_address": str(client_address)}
                        await websocket.send(json.dumps(echo_response))
                    else:
                        logging.warning(f"Received unknown message type from {client_address}: {message_type}")
                        error_message = {"type": "error", "message": f"Unknown message type: {message_type}"}
                        await websocket.send(json.dumps(error_message))
                elif conf.SERVER_TYPE == 'filesys':
                    payload = data.get("file")
                    if message_type == "get":
                        # Get a file from the './file/server/' folder
                        temporary_data = ''
                        try:
                            with open(payload, 'r') as file:
                                temporary_data = file.read()
                            code = '200'
                        except:
                            temporary_data = ''
                            code = '404'
                        echo_response = {"type": "get_response", "file": payload, "sender_address": str(client_address), 
                                         "data": temporary_data, "code": code}
                        await websocket.send(json.dumps(echo_response))
                    elif message_type == "post":
                        # Create/write a file to the './file/server/' folder
                        temporary_data = payload = data.get("data")
                        try:
                            with open(payload, 'w') as file:
                                file.write(temporary_data)
                            code = '201'
                        except:
                            code = '404'
                        echo_response = {"type": "post_response", "file": payload, "sender_address": str(client_address), 
                                         "data": "", "code": code}
                        await websocket.send(json.dumps(echo_response))
                    else:
                        logging.warning(f"Received unknown message type from {client_address}: {message_type}")
                        error_message = {"type": "error", "message": f"Unknown message type: {message_type}"}
                        await websocket.send(json.dumps(error_message))

            except json.JSONDecodeError:
                logging.error(f"Received invalid JSON from {client_address}: {message}")
                error_message = {"type": "error", "message": "Invalid JSON format"}
                await websocket.send(json.dumps(error_message))
            except Exception as e:
                logging.error(f"Error processing message from {client_address}: {e}")
                error_message = {"type": "error", "message": f"Error processing message: {e}"}
                await websocket.send(json.dumps(error_message))

    except websockets.ConnectionClosedError:
        logging.info(f"Connection with {client_address} closed unexpectedly")
    except websockets.ConnectionClosedOK:
        logging.info(f"Connection with {client_address} closed normally")
    finally:
        # Remove the client from the set when the connection is closed
        connected_clients.remove(websocket)
        logging.info(f"Client disconnected from {client_address}")

async def broadcast_message(message, sender_address, btype, user):
    """
    Broadcasts a message to all connected clients except the sender.

    Args:
        message (str): The message to broadcast.
        sender_address (str): the address of the sender.
    """
    if not connected_clients:
        logging.info("No clients connected, not broadcasting message.")
        return

    logging.info(f"Broadcasting message from {sender_address}: {message}")
    for client in connected_clients:
        # Avoid sending the message back to the sender.
        if client.remote_address != sender_address:
            try:
                broadcast_message = {"type": btype, "sender": sender_address, "payload": message, "user": user,
                                     "server_appn": conf.SERVER_DISPLAY_NAME}
                await client.send(json.dumps(broadcast_message))
            except websockets.ConnectionClosed:
                logging.info(f"Connection with {client.remote_address} is closed, skipping.")
            except Exception as e:
                logging.error(f"Error sending message to {client.remote_address}: {e}")

async def start_server(host, port):
    """Starts the WebSocket server"""

    async with websockets.serve(handle_client, host, port) as server:
        logging.info(f"WebSocket server started at ws://{host}:{port}")
        await server.wait_closed()
    logging.info("WebSocket server stopped.")

global console_popup

def on_closing():
    console_popup.destroy()
    sys.exit()

if __name__ == "__main__":
    HOST = conf.IP  # 0.0.0.0 to listen on all interfaces
    PORT = 8765

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    console_popup = ConsolePopup(root)
    console_popup.protocol("WM_DELETE_WINDOW", on_closing)
    sys.stdout = RedirectedConsole(console_popup)

    console_popup.show()

    threading.Thread(target=background_task, args=(console_popup,), daemon=True).start()
    
    root.mainloop()
