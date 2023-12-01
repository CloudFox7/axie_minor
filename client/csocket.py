import socket
import threading
from audio_windows import Audio
import json
from datetime import datetime
import sys,os
from network import send_json as spost,get_json as sget
sys.path.append('..\\')
from application.raspi_connector.connector import Device_Connector
class Action:
    def __init__(self) -> None:
        self.busy = False
        self.saving = False
        self.alerting = False
        self.audio = Audio()
        self.actions = {
            0 : self.audio.detected_user,
            1 : self.audio.convert,
            2 : self.audio.speak_text #custom text
        }
        self.queue = []
        self.request = None

    def idleQueueTimer(self):
        while True:
            now = datetime.now()

            while (datetime.now() - now).seconds < 3 and not self.busy:pass
            if (datetime.now() - now).seconds >= 3 and not self.busy and androidDevice.gethome():
                print("system idle processing contacts ...")
                self.request = True
                listc = sget('getlist')["list"]
                if len(listc) < 1 : continue
                self.queue.append({
                    "key":1,
                    "param":listc
                })
                return

    def addAction(self,act:dict):
        self.queue.append(act)
    def getActions(self):
        if not self.busy:
            return self.actions
        return None
    

    def actionQueue(self):
        while True:
            if self.queue != []:
                message = self.queue[0]
                if message["param"]:
                    res = self.actions[message["key"]](message["param"])
                else:
                    res = self.actions[message["key"]]()
                if res and message["key"] ==1:
                    spost('contacts',res)
                print("Action processed")
                self.queue.pop(0)

class Client_Socket:
    def __init__(self,actionobj) -> None:
        self.act = actionobj
        host = socket.gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number
        self.client_socket = socket.socket()  # instantiate
        self.client_socket.connect((host, port)) 
        self.socketbusy = False
    def listen_to_socket(self):
        while True:
            while self.socketbusy:pass
            self.socketbusy = True
            data = self.client_socket.recv(1024).decode()
            self.client_socket.send('ack'.encode())
            self.socketbusy = False
            print(data)
            data = json.loads(data)
            print('Received from server: ' + str(dict(data)))
            if dict(data)["action"]:
                self.act.addAction(dict(dict(data)["arg"]))
            else:
                print(dict(data)["message"])




if __name__ == '__main__':
    action = Action()
    androidDevice = Device_Connector()
    csckt= Client_Socket(action)
    threading.Thread(target=androidDevice.startService,daemon=True).start()
    threading.Thread(target=csckt.listen_to_socket,daemon=True).start()
    threading.Thread(target=action.idleQueueTimer,daemon=True).start()
    action.actionQueue()