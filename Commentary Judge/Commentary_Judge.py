from cmd import PROMPT
from pyclbr import Class
import pyaudio
import numpy as np
import time
import audioop
import obspython as obs
import Play_Audio_Commentary as play
import random
import os
import ctypes
import sounddevice as sd
import soundfile as sf


########### VARIABLES ############

# PyAudio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

class Variables:
    def __init__(self):
        self.iT = 0
        self.timer = 0
        self.speakingCount = 0
        self.maxTime = 0
        self.toggle = None
        self.sourceName = "Speach Light (Tome)"
        self.redCount = 0
        self.detect = None
        self.image = "sound indicator.png"
        self.red = "Red"
        self.green = "Green"
        self.device = ""

        #Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        self.inputDevice = 1
        #Open stream
        self.inputData = self.audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index= self.inputDevice,
                        frames_per_buffer=CHUNK)

class Prompts:
    def __init__(self, audio):
        self.audio = audio

v = Variables()

#Dictionary of audio files use
prompt_dict = {
    1: Prompts("1"),
    2: Prompts("2"),
    3: Prompts("3"),
    4: Prompts("4"),
    5: Prompts("5"),
    6: Prompts("6"),
    7: Prompts("7")
    }


########### OBS BUTTONS ############

def toggle_countdown(props, prop):


    #Stop Countdown
    if v.toggle:
        obs.timer_remove(listen)
        obs.timer_remove(is_talking)
        v.toggle = False
        v.detect = False
        v.iT, v.timer, v.speakingCount = 0, 0, 0,      #reset count variables to 0
        print("Countdown Stopped")
    #Start countdown 
    else: 
        #Check for valid Audio Device
        try: 
            sd.check_output_settings(v.device)
        except:
            print("You need to enter a valid Audio Device")
            return

        print("Max Time: " + str(v.maxTime/10) + "s")
        print("Listening...")
        obs.timer_add(listen, 100)
        v.toggle = True

def add_light(props, Prop):
    settings = obs.obs_data_create()
    create_light(settings)
    obs.obs_data_release(settings)


########### FUNCTIONS ############

#Open input stream
def input_stream(inputDevice):
    v.inputData = v.audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index= inputDevice,
                        frames_per_buffer=CHUNK)

#Find db value from the root mean square
def rms_to_db(rms, reference=32767):
    return 20 * np.log10(rms / reference)

def is_speaking(instream):
    
    # Read audio data from the microphone
    data = np.frombuffer(instream.read(CHUNK), dtype=np.int16)   
    if data.size > 0:
        # Compute audio level (root mean square)
        rms = audioop.rms(data, 2)
        db_value = rms_to_db(rms)
        if db_value > -35:                    
            #print(f"RMS Value: {rms}, dB Value: {db_value:.2f} dB")
            light(True)
            v.redCount = 0
            return True
        else:
            #some nonsense to stop the light from flashing rapidly when talking
            if v.redCount >= 10:
                light(False)
                v.redCount = 0
            else:
                v.redCount += 1
            return False
    else:
        print("No audio data received.")

#Function to change the filter on the "light" source from red to green
def light(On):
    source = obs.obs_get_source_by_name(v.sourceName)
    sourceFilterGreen = obs.obs_source_get_filter_by_name(source, v.green)
    sourceFilterRed = obs.obs_source_get_filter_by_name(source, v.red)
    obs.obs_source_set_enabled(sourceFilterGreen, On)
    obs.obs_source_set_enabled(sourceFilterRed, not On)
    obs.obs_source_release(source)

def listen():
    if v.detect:        #Boolean to detect is secondary timer is already running so not to activate it again
        v.timer += 1    #increment main timer
    else:
        if is_speaking(v.inputData):
            print("Detected sound")
            #create new timer for "is_talking" to distinguish if speaking long enough to be considered talking/commentary
            obs.timer_add(is_talking, 100)
            v.detect = True
        else:
            v.timer += 1            
    
    #check if countdown has ended
    if v.timer >= v.maxTime:
        v.maxTime = round((v.maxTime/2) + 5)
        v.timer = 0
        print("you stopped talking, the timer has decreased to:" + str(v.maxTime/10) + "s")

        #play random audio file
        entry = random.randint(1, len(prompt_dict))
        fileName = f"Motivation/{prompt_dict[entry].audio}.wav"
        play.play_audio_sd(fileName, v.device)


def is_talking():
    #Check if speaking long enough over 5 seconds to be considered talking.
    if v.iT < 50:
        if is_speaking(v.inputData):
            v.speakingCount += 1    #count every time a sound is detected
        v.iT += 1                   #increment sub timer (talking check)
    #Once 5 seconds has passed check if "speakingCount" is higher enough and reset main timer if True.
    elif v.iT >= 50:
        if v.speakingCount >= 25:            
            v.timer = 0
            v.speakingCount = 0
            print("Countdown Reset")

        v.iT = 0
        v.detect = False
        obs.timer_remove(is_talking)    #remove current timer

def create_light(settings):
    #create the image source for the light
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)
    sourceLight = obs.obs_source_create("image_source", v.sourceName, settings, None)
    obs.obs_scene_add(scene, sourceLight)

    #add image to source
    imagePath = get_file_path(v.image)
    obs.obs_data_set_string(settings, "file", imagePath)
    obs.obs_source_update(sourceLight, settings)

    #add the red filters to the light source
    obs.obs_data_set_int(settings, "color", 0x0000e1)
    filter_red = obs.obs_source_create_private("color_filter", v.red, settings)
    obs.obs_source_filter_add(sourceLight, filter_red)
    
    #add the green filter
    obs.obs_data_set_int(settings, "color", 0x44b100)
    filter_green = obs.obs_source_create_private("color_filter", v.green, settings)
    obs.obs_source_filter_add(sourceLight, filter_green)
    #hide green filter
    obs.obs_source_set_enabled(filter_green, False)

    #release
    obs.obs_scene_release(scene)
    obs.obs_source_release(sourceLight)
    obs.obs_source_release(filter_green)
    obs.obs_source_release(filter_red)

#Get the file path in which the file "fileName" is stored.
def get_file_path(fileName):
    # Get the current directory (where the script is located)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Name of the file you're searching for
    target_file_name = fileName

    # Construct the full path to the target file
    target_file_path = os.path.join(script_directory, target_file_name)
    #Create the folder "obs-countdown" if it doesn't already exist.
    if not os.path.exists(target_file_path):
        print(".txt File not found in the script directory.")
    return target_file_path

#Create a list of all output audio devices
def output_device_list(pList):
    dictEntries = len(sd.query_devices())
    i = 0
    while i < dictEntries:          #can't use a for loop, clashes with tuple
        device_info = sd.query_devices()[i]
        device_name = device_info['name']
        hostapi = device_info['hostapi']
        inputChannels = device_info['max_input_channels']
        if hostapi == 0 and inputChannels == 0:
            hostapi_type = sd.query_hostapis()[hostapi]['name']  # Fetch host API name
            # Combine the information to reconstruct the desired string
            formatted_device_string = f" {device_name}, {hostapi_type}"
            obs.obs_property_list_add_string(pList, formatted_device_string, str(i))
        i += 1 

#Create a list of all input audio devices
def input_device_list(pList):
    dictEntries = len(sd.query_devices())
    i = 0
    while i < dictEntries:          #can't use a for loop, clashes with tuple
        device_info = sd.query_devices()[i]
        device_name = device_info['name']
        hostapi = device_info['hostapi']
        outputChannels = device_info['max_output_channels']
        if hostapi == 0 and outputChannels == 0:
            hostapi_type = sd.query_hostapis()[device_info['hostapi']]['name']  # Fetch host API name
            # Combine the information to reconstruct the desired string
            formatted_device_string = f"{device_name}, {hostapi_type}"
            device_index = str(i)
            obs.obs_property_list_add_string(pList, formatted_device_string, device_index)
        i += 1 




########### OBS SCRIPT FUNCTIONS ############

#description of programme for OBS
def script_description():
    return  "<h1>Tome's Speach Motivator</h1>" + \
            "Python script for listening to motivate you to talk more by shouting at you if you don't." + \
            "<br/>" +\
            "----------------------------------------------------------"  

def script_update(settings):
    timeSlider = obs.obs_data_get_int(settings, "slider")
    v.device = int(obs.obs_data_get_string(settings, "output"))

    v.inputDevice = int(obs.obs_data_get_string(settings, "input"))
    input_stream(v.inputDevice)
    v.maxTime = timeSlider * 600                            #convert time from minutes to deciseconds
    #v.maxTime = 20                                         #for testing
    
def script_properties():
    props = obs.obs_properties_create()

    outputList = obs.obs_properties_add_list(props, "output", "Output Devices", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    output_device_list(outputList)
    inputList = obs.obs_properties_add_list(props, "input", "Input Devices", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    input_device_list(inputList)

    obs.obs_properties_add_int_slider(props, "slider", "Max Time", 1, 10, 1)    #slider for maximum time in minutes
    obs.obs_properties_add_button(props, "toggle", "Start/Stop", toggle_countdown)
    obs.obs_properties_add_button(props, "light", "Add Light", add_light)

    return props

def script_unload():
    #don't know what these exactly do but seems smart to close everything when the programme is closed
    v.inputData.stop_stream()
    v.inputData.close()
    v.audio.terminate()