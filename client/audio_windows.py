import pyaudio
import wave
import pyttsx3
import speech_recognition as sr
from datetime import datetime

class Audio:
    def __init__(self) -> None:
        self.p = pyaudio.PyAudio()
        self.r = sr.Recognizer() 
        self.engine = pyttsx3.init()

    def speak_text(self,text:str):
        print("Machine : ",text)
        self.engine.say(text)
        self.engine.runAndWait()
        print("return")
    
    def speech_to_text(self):
        while True:
            try:
                with sr.Microphone() as source2:
                    self.r.adjust_for_ambient_noise(source2, duration=0.2)
                    print("Process : Speak")
                    audio2 = self.r.listen(source2)
                    MyText = self.r.recognize_google(audio2)
                    MyText = MyText.lower()
                    print("Assisted : ",MyText)
                    return MyText
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
            except sr.UnknownValueError:
                print("unknown error occurred")
    
    def convert(self,ids):
        sheet = dict()
        self.speak_text("Device Idle Starting Profile Conversion")
        self.speak_text(str("You have a total of " + str(len(ids)) + " contacts to save !, say yes to confirm"))
        response = self.speech_to_text()
        if 'yes' in response or 'proceed' in response:
            self.speak_text('Alright Lets start')
            for i in ids:
                time = datetime.fromtimestamp(float(i.replace('guy','')))
                if time.date() == datetime.now().date():
                    day = " Today"
                else:
                    day = " on " + str(time.date().day)
                self.speak_text('You met this person at ' + str(time.hour) + day)
                cnf = False
                while not cnf:
                    self.speak_text('want me to save it as ?')
                    name =  self.speech_to_text()
                    if 'cancel' in name:
                            self.speak_text('okay cancelling contact creation process')
                            return sheet
                    self.speak_text('confirm name, selected name ' + name)
                    confim = self.speech_to_text()
                    if 'confirm' in confim:
                        cnf = True
                        self.speak_text('saving this person as : ' + name)
                        sheet[i] = name
            return sheet
        else:
            print("Process Cancelled")
            self.speak_text("cancelling operations")
        return False

    def detected_user(self,name):
        print("speaking located user")
        self.speak_text("Located " + str(name))
        
    def record(self,duration=10,record_name="output.wav"):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = duration
        WAVE_OUTPUT_FILENAME = record_name
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("* recording")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("* done recording")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

if __name__ == "__main__":
    audio = Audio()
    report = audio.convert(['1700897329guy'])
    print("Process : ",report)