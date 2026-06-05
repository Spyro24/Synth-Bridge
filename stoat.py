import wssClient
import threading
import time
import json
import requests

class stoatBridge:
    def __init__(self):
        self.name = "stoat"
        self.channels = []
        self.botToken = ""
        self.messageStack = []
        self.platforms = []
    
    def insertMessage(self, message):
        self.messageStack.append(message)
    
    def run(self):
        self.websocket = wssClient.WSSClient(f"wss://stoat.chat/events?version=1&format=json&token={self.botToken}")
        self.nextPing = time.time() + 10
        time.sleep(2)
        def work_thread():
            loop = True
            while loop:
                if self.websocket.has_new_data():
                    for packet in self.websocket.get_messages():
                        packet = json.loads(packet)
                        if packet["type"] == "Message" and "content" in packet:
                            try:
                                messagePack = {"content": packet["content"], "emiter": self.name, "channel": self.channels.index(packet["channel"])}
                                for platform in self.platforms:
                                    platform.messageStack.append(messagePack)
                            except ValueError: pass
                if len(self.messageStack) > 0:
                    self.sendMessage(self.messageStack.pop())
                if self.nextPing < time.time():
                    self.websocket.send_data('{"type":"Ping","data":' + str(time.time()) + '}')
                    self.nextPing = time.time() + 10
        print("Stoat Ready")
        self.thread = threading.Thread(target=work_thread, daemon=True)
        self.thread.start()
    
    def sendMessage(self, mesagePack):
        if mesagePack["emiter"] != self.name:
            sendJson = {"content": mesagePack["content"]}
            if "userData" in mesagePack:
                masqData = {"name": mesagePack["userData"]["userName"], "avatar": mesagePack["userData"]["avatar"]}
                sendJson["masquerade"] = masqData
            requests.post(f"https://stoat.chat/api/channels/{self.channels[mesagePack['channel']]}/messages?", headers={"X-Bot-Token": self.botToken}, json=sendJson)