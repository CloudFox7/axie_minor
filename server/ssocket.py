import socket
import json
from threading import Thread
import os
class SSocket:

    def server_program(self):
        # get the hostname
        host = socket.gethostname()
        port = 5000  
        self.needsocket = False
        self.socketbusy = False
        self.server_socket = socket.socket()  
        self.server_socket.bind((host, port))
        print("listening on .. ",host,":",port) 
        self.server_socket.listen(10)
        Thread(target=self.connectors).start()
        
    def connectors(self):
        while True:
            self.conn, self.address = self.server_socket.accept() 
            print("Connection from: " + str(self.address))
            self.sendmessage("Connection Established !")
            self.sendaction(key=2,arg="Connected to server")

                

    def sendmessage(self,message):
        json_v = {
                    "action":False,
                    "message":str(message)
        }
        while self.socketbusy:self.needsocket = True
        self.socketbusy = True
        self.conn.send(json.dumps(json_v).encode())
        self.conn.recv(1024)
        self.socketbusy = False
        self.needsocket = False

    def sendaction(self,key,arg=False):
        json_v = {
            "action":True,
            "arg":{
                "key":key,
                "param":arg
            },
            "message":"action inbound"
        }
        
        while self.socketbusy:self.needsocket = True
        self.socketbusy = True
        self.conn.send(json.dumps(json_v).encode())  # send data to the client
        self.conn.recv(1024)
        self.socketbusy = False
        self.needsocket = False

    def __del__(self):
        self.conn.close()


class Action:
    def __init__(self) -> None:
        self.scon = SSocket()
        Thread(target=self.scon.server_program,daemon=True).start()
        print("socket started")

    def cleaner(self):
        while True:
            try:
                if os.path.exists('edits'):
                    var =  os.listdir('edits')
                    for folder in var:
                        path = os.path.join(os.getcwd(),'edits',folder)
                        if len(os.listdir(path)) > 0:
                            pass
                        else:
                            os.remove(path)
            except Exception as e:
                print(e)

    def threadclean(self):
        Thread(target=self.cleaner,daemon=True).start()
    def located_user(self,names):
        if len(names) > 1 :
            names = ','.join(names)
        elif len(names) == 1:
            names = str(names[0])
        else:
            return
        self.scon.sendaction(key=0,arg=str(names))



