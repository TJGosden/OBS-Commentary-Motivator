from email.mime import audio
from random import sample
from tkinter import*
import sounddevice
import threading
import soundfile
import os

################################################################################################

DATA_TYPE = "int16"

#Create Thread to play audio
class myThread(threading.Thread):
    def __init__(self, stream, song):
        threading.Thread.__init__(self)              
        self.stream = stream
        self.song = song
    def run(self):
        playThread(self.stream, self.song)

def playThread(stream, song):
    stream.outstream.write(song.music)

#Create object for data from audio file
class musicData:
    def __init__(self, path):
        self.music, self.samplerate = load(path)

def load(path):
    audio_data, samplerate = soundfile.read(path, dtype=DATA_TYPE)
    return audio_data, samplerate

#Create object for all the audio data as a "RawOutputStream"
class streamData:
    def __init__(self, index, samplerate):
        self.outstream = create(index, samplerate)

def create(index, samplerate):
    output = sounddevice.RawOutputStream(
        device = index,             #The choosen output device
        dtype = DATA_TYPE,          #The sample format
        #CHANGE THIS IF THERE ARE AUDIO PROBLEMS, mono "1", or stereo "2" 
        channels = 1,               #Number of Channels of sound to be delivered to the stream 
        samplerate = samplerate,    #Speed of audio file (frequency)
        )
    return output


############################## MAIN FUNCTION ##############################

def play_audio_sd(targetFileName, index):
    #Get File path
    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    targetFilePath = os.path.join(scriptDirectory, targetFileName)
    #Initialise the data and "RawOutputStream"
    song = musicData(targetFilePath)
    stream = streamData(index, song.samplerate)
    #Create Thread
    thread = myThread(stream, song)
    stream.outstream.start()
    #Play audio file
    thread.start()
