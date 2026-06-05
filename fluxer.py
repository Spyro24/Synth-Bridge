import wssClient
import threading
import time
import json
import requests
import random

class Bridge:
    def __init__(self):
        self.name = "fluxer"
        self.channels = []
        self.botToken = ""
        self.messageStack = []
        self.platforms = []
        self.nextHeartBeat = time.time() + 200
        self.HeartBeatInterval = None
        self.lastHeartBeatSequence = None
    
    def insertMessage(self, message):
        self.messageStack.append(message)
    
    def run(self):
        self.websocket = wssClient.WSSClient(f"wss://gateway.fluxer.app/?v=1&encoding=json&compress=zstd-stream")
        self.jsonEncoder = json.encoder.JSONEncoder()
        self.jsonDecoder = json.decoder.JSONDecoder()
        time.sleep(2)
        self.websocket.send_data(self.jsonEncoder.encode({"op":2,"d":{"token":self.botToken, "properties": {"os": "linux", "browser": "synth_bridge", "device": "desktop"}, "intents": 7}}))
        self.websocket.send_data(self.jsonEncoder.encode({"op": 1, "d": None}))
        def work_thread():
            #try:
                loop = True
                while loop:
                    if self.websocket.has_new_data():
                        for packet in self.websocket.get_messages():
                            print(packet)
                            packet = json.loads(packet)
                            if packet["op"] == 10:
                                self.HeartBeatInterval = packet["d"]["heartbeat_interval"] / 1000
                                self.nextHeartBeat = time.time() + self.HeartBeatInterval * random.random()
                                self.websocket.send_data(self.jsonEncoder.encode({"op": 1, "d": self.lastHeartBeatSequence}))
                            elif packet["op"] == 0:
                                if packet["t"] == "MESSAGE_CREATE":
                                    msg = packet["d"]
                                    try:
                                        messagePack = {"content": msg["content"], "emiter": self.name, "channel": self.channels.index(msg["channel_id"])}
                                        for platform in self.platforms:
                                            platform.messageStack.append(messagePack)
                                    except ValueError: pass
                    if time.time() > self.nextHeartBeat:
                        self.websocket.send_data(self.jsonEncoder.encode({"op": 1, "d": self.lastHeartBeatSequence}))
                        self.nextHeartBeat = time.time() + self.HeartBeatInterval * random.random()
                        
                            
            #except:
                print("Fluxer Failed")
        print("Fluxer Ready")
        self.thread = threading.Thread(target=work_thread, daemon=True)
        self.thread.start()
    
    def sendMessage(self, mesagePack):
        if mesagePack["emiter"] != self.name:
            pass