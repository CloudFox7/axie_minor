from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image
import cv2
import time
import os
from ssocket import Action
from idleservices import Idle_server
class ProfileManager:
    def __init__(self,defined) -> None:
       
        self.contacts = dict()
        for contact in defined:
            self.contacts[contact] = [False,0] #setting deafault missing user frame occurance of a user to "zero"
            #this class manages user occurance and thereby alerting nodes, 
            #while preventing any duplicated, works by contact name as contact id as of now
        self.anonymous = dict()
        self.framecount = 10
    
    def located_known(self,namelist):
        locatedlist = []
        if self.framecount == 0:
            self.framecount = 10
        else: self.framecount = self.framecount - 1
        not_in_frame = list(self.contacts.keys())
        for contact in namelist:
            not_in_frame.remove(contact)
            if not self.contacts[contact][0]:
                self.contacts[contact][1] = 0
                self.contacts[contact][0] = True
                locatedlist.append(contact)
                print("Hey, ",contact," is here !")
                continue
            #user was not +found even after frames !
        if locatedlist:
            action.located_user(locatedlist)   
        for user in not_in_frame:
            if self.contacts[user][1] > 100 and self.contacts[user][0]:
                self.contacts[user][0] = False
                print("soo long ",user, " never saw him removing his active alerts")
            self.contacts[user][1] += 2

    def unknown_ids(self,namelist):
        renderx = []
        for contact in namelist:
            if contact in self.anonymous.keys():
                self.anonymous[contact][0] += 1
                if self.anonymous[contact][0] >= 10 and not self.anonymous[contact][1]:
                    renderx.append(namelist)
                    self.anonymous[contact][1] = False
                    self.anonymous[contact][0] = 4
            else:
                self.anonymous[contact][0] = 1
                self.anonymous[contact][1] = False
        return renderx #this is list of all the unknown users whose 10 frames were located !
        # this checkers first time 10, next all are 10-4 = 6 frames
        



            


class WebCamProcess:
    def __init__(self,source) -> None:
        self.source = source
        self.mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False, min_face_size=40) # keep_all=False
        self.mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40) # keep_all=True
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.contacts = dict()
        self.profile = None

    def collate_fn(self,x):
        return x[0]
    
    def torchExport(self,folder='photos',savefile='data.pt'):
        dataset = datasets.ImageFolder(folder)
        idx_to_class = {i:c for c,i in dataset.class_to_idx.items()}
        loader = DataLoader(dataset, collate_fn=self.collate_fn)
        name_list = [] 
        embedding_list = [] 
        for img, idx in loader:
            face, prob = self.mtcnn0(img, return_prob=True) 
            if face is not None and prob>0.90:
                emb = self.resnet(face.unsqueeze(0)) 
                embedding_list.append(emb.detach()) 
                name_list.append(idx_to_class[idx])        
        data = [embedding_list, name_list]
        if folder == 'photos':
            self.profile = ProfileManager(name_list)
        torch.save(data, savefile)
        return embedding_list,name_list
    
    def predictFace(self,embedding_list,emb):
        dist_list = [] # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        if dist_list:
            min_dist = min(dist_list) 
            min_dist_idx = dist_list.index(min_dist) # get minumum dist index
        return min_dist,min_dist_idx
    
    def liveReload(self,emb):

        embedding_list_live,name_list_live = self.torchExport(folder='edits',savefile='edits.pt')
        distance,index = self.predictFace(embedding_list=embedding_list_live,emb=emb)
        if distance > 0.9:
            return (False,distance)
        name = name_list_live[index]
        return (True,name)
    


    def startScanningFaceRecognition(self):
        embedding_list,name_list = self.torchExport()
        cam = cv2.VideoCapture(self.source)
        index_persistence = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #simple variable to make sure we get face alteast for a fixed frame count before algo works
        while True:
          try:  
            ret, frame = cam.read()

            if not ret:
                print("fail to grab frame, try again")
                break

            img = Image.fromarray(frame)
            img_cropped_list, prob_list = self.mtcnn(img, return_prob=True) 
            if img_cropped_list is not None:
                boxes, _ = self.mtcnn.detect(img)
                contact_list_recored = []
                uks_ids = []
                # for i in range(len(prob_list),len(index_persistence)):
                #     index_persistence[i] = 0 #reset persistance
                for i, prob in enumerate(prob_list):
                    if prob > 0.90:
                        index_persistence[i] += 1
                        emb = self.resnet(img_cropped_list[i].unsqueeze(0)).detach() 
                        dist_list = [] # list of matched distances, minimum distance is used to identify the person

                        for idx, emb_db in enumerate(embedding_list):
                            dist = torch.dist(emb, emb_db).item()
                            dist_list.append(dist)

                        min_dist,index = self.predictFace(embedding_list=embedding_list,emb=emb) # get minumum dist value
                        min_dist_idx = dist_list.index(min_dist) # get minumum dist index
                        name = name_list[index] # get name corrosponding to minimum dist
                        box = boxes[i] 
                        original_frame = frame.copy() # storing copy of frame before drawing on it
                        #handling detections, this code runs only if a face was found rest is whose face
                        
                        if min_dist < 0.9: #located a face (from contacts)
                            frame = cv2.putText(frame, name+' '+str(min_dist), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)
                            contact_list_recored.append(name)
                            index_persistence[i] = 0

                        else:
                            if index_persistence[i] > 10:
                                index_persistence[i] = 0
                                vector = original_frame[int(box[1]):int(box[3]),int(box[0]):int(box[2])]
                                res = [False,'FailedVector']
                                try:res = self.liveReload(emb=emb)
                                except:print("vector reload failed")
                                uks_ids.append(res[1])
                                if res[0]:
                                    print("Reappearing unknown : ",res[1])
                                    frame = cv2.putText(frame, res[1]+' '+str(min_dist), (int(box[0]),int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),1, cv2.LINE_AA)
                                    img_name = "edits/{}/{}.jpg".format(res[1], int(time.time()))
                                    cv2.imwrite(img_name, vector)
                                else:
                                    print("Random Person ",res[1])    
                                    random = str(int(time.time()))
                                    if not os.path.exists('edits/'+random+'guy'):
                                        os.mkdir('edits/'+random+'guy')
                                    try:
                                        img_name = "edits/{}/{}.jpg".format(random+'guy', int(time.time()))
                                        cv2.imwrite(img_name, vector)
                                    except:os.removedirs('edits/'+random+'guy')
                        frame = cv2.rectangle(frame, (int(box[0]),int(box[1])) , (int(box[2]),int(box[3])), (255,0,0), 2)
                    try:
                        self.profile.located_known(contact_list_recored)
                    except:
                        print("Profile Bounds")
          except Exception as e:
              print("Frame Failure",e)
              
          k = cv2.waitKey(1)
          cv2.startWindowThread()

          cv2.imshow("IMG", frame)
        #   try:cv2.imshow("ORG",original_frame)
        #   except NameError:print("ORG REFER FAIL")
        #   try:
            #   cv2.imshow("IMG2", vector)
        #   except:pass
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    action = Action()
    idle = Idle_server()
    idle.compute()
    action.threadclean()
    input("Hit Enter to start scanning ...")
    scanner = WebCamProcess(0)
    scanner.startScanningFaceRecognition()


