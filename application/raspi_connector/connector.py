
from flask import Flask, request, jsonify
from flask_cors import CORS


class Device_Connector:
      def __init__(self):
            self.home = None
            self.app = Flask(__name__)
            self.app.config['CORS_HEADERS'] = 'Content-Type'
            cors = CORS(self.app)
            @self.app.route('/')
            def hello_world():
                return "Android CONN API"

            @self.app.route('/location', methods=['POST'])
            def home_devices_post():
                    record = request.json
                    self.home = dict(record)["location"]
                    print("Location factor updated to : " ,self.home)
                    return jsonify({"status":"ok"})
      def gethome(self):
            return self.home
      def startService(self):
           print("starting server ...")
           self.app.run('0.0.0.0')
        
      
if __name__ == "__main__":
      from threading import Thread
      mobiledev = Device_Connector()
      Thread(target=mobiledev.startService,daemon=True).start()
      while True:
            
            if mobiledev.gethome():
                print(mobiledev.gethome())
      
