
from flask import Flask, request, jsonify
from flask_cors import CORS
import os,threading,json

class Idle_server:
      def __init__(self):
            self.busy = False
            self.app = Flask(__name__)
            @self.app.route('/')
            def hello_world():
                return "IDLE CONN API"

            @self.app.route('/getlist')
            def getlist():
                folders = os.listdir('edits')
                lists = []
                for folder in folders:
                     try:
                          float(folder.replace('guy',''))
                          lists.append(folder)
                     except Exception as e:
                          print(e)
                print("Folders  : ",lists)
                return jsonify({
                     "list" : lists
                })
            
            @self.app.route('/contacts', methods=['POST'])
            def home_devices_post():
                    if self.busy:
                         return jsonify({"status","busy"})
                    self.busy = True
                    record = request.data
                    record = json.loads(record)

                    sheet = dict(record)
                    print(sheet)
                    try:
                        for k,v in sheet.items():
                            print("parsing ",k,v)
                            os.rename(os.path.join(os.getcwd(),'edits',k),os.path.join(os.getcwd(),'photos',v))
                    except Exception as e:
                          print(e)
                    self.busy = False
                    return jsonify({"status":"ok"})
            
      def startService(self):
           print("starting server ...")
           self.app.run('0.0.0.0',9999)
      def compute(self):
           threading.Thread(target=self.startService,daemon=True).start()
        
      
      
