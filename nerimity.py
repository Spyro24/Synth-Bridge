import wssClient
import threading
import requests
import time
import json

class Bridge:
    def __init__(self):
        self.name = "nerimity"
        self.channels = []
        self.botToken = ""
        self.messageStack = []
        self.platforms = []
    
    def insertMessage(self, message):
        self.messageStack.append(message)
    
    def run(self):
        self.websocket = wssClient.WSSClient("wss://nerimity.com/socket.io/?EIO=4&transport=websocket")
        time.sleep(2)
        self.websocket.send_data("40")
        self.websocket.send_data('42["user:authenticate",{"token":"' + self.botToken + '"}]')
        self.botID = requests.get("https://nerimity.com/api/users", headers={"Authorization": self.botToken}).json()["user"]["id"]
        def work_thread():
            loop = True
            while loop:
                if self.websocket.has_new_data():
                    for package in self.websocket.get_messages():
                        if package == "2":
                            self.websocket.send_data("3")
                        else:
                            try:
                                data = json.loads(package[2:])
                                print(data)
                                if "message:created" in data:
                                    msgData = data[1]
                                    try:
                                        if msgData["message"]["createdById"] != self.botID:
                                            creatorData = msgData["message"]["createdBy"]
                                            userData = {"userName": creatorData["username"], "avatar": "https://cdn.nerimity.com/" + creatorData["avatar"]}
                                            messagePack = {"content": msgData["message"]['content'], "emiter": self.name, "channel": self.channels.index(msgData["message"]['channelId']), "userData": userData}
                                            for platform in self.platforms:
                                                platform.messageStack.append(messagePack)
                                    except ValueError: pass
                            except json.decoder.JSONDecodeError:
                                print(package)
                if len(self.messageStack) > 0:
                    self.sendMessage(self.messageStack.pop())
        print("Nerimity Ready")
        self.thread = threading.Thread(target=work_thread, daemon=True)
        self.thread.start()
    
    def sendMessage(self, mesagePack):
        if mesagePack["emiter"] != self.name:
            msg = {"content": mesagePack["content"]}
            if "userData" in mesagePack:
                msg["username_override"] = mesagePack["userData"]["userName"]
                msg["avatar_url_override"] = mesagePack["userData"]["avatar"]
            requests.post(f"https://nerimity.com/api/channels/{self.channels[mesagePack['channel']]}/messages", headers={"Authorization": self.botToken}, data=msg)