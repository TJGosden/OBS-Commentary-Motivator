# OBS-Commentary-Motivator
This Python programme will help motivate you to talk while streaming using OBS.

# How to Use
To use this programme, download the "Commentary Judge" file, then you must add the **"Commentary_Judge.py"** file to your OBS **"Scripts"** tabs which can be found under "Tools". **You'll also need to install the following libraires: pyaudio, audioop, sounddevice, soundfile.**

![Settings](Motivator_Gui.JPG)

# Setup
- First, you'll need to set your input and output devices (I'm not confident in my audio knowledge so please let me know if there is a problem).
- Optional: By pressing the "add light" button, you can add an image into your obs that will indicate if you are talking. This will create a new source called "Speach Light (Tome)" with two filters "red" and "green". Do what you like with this, i.e. resize, change filter colours, change image, etc.
- Set the "max time" to whatever amount of time you realistically go without talking on stream.
- Press start to begin.

# What does the "Commentary Motivator" actually do?
When you start the programme, it will start counting down from the "max time" you set and will listen to your mic for when you talk. Once the programme hears a sound it will gauge over 5 seconds whether you have been speaking enough to be considered talking. If this is the case the countdown will be reset. However, if you don't talk enough and the countdown times out, the max time will then be cut in half and you will be chastised. So try your best to keep the countdown from becoming unmanageably short. 
