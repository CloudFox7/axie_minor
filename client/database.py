import pickle

class DataBase:
    def __init__(self,name='userdb',database={}) -> None:
            self.name = name
            self.db = database
            self.loadDatabase()
    def saveDataBase(self):
        dbfile = open(self.name, 'wb')
        pickle.dump(self.db, dbfile)
        dbfile.close()

    def loadDatabase(self):
        try:
            dbfile = open(self.name, 'rb')
            self.db = pickle.load(dbfile)
            dbfile.close()
        except FileNotFoundError:
            print("no database located")
            self.db = {}
            pass

    def getdb(self):
         return self.db
    
    def updatedb(self,db):
         self.db = db
         self.saveDataBase()
