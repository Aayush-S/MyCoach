from flask import Flask, render_template, request, redirect

import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import wavio
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


app = Flask(__name__)

authenticator = IAMAuthenticator('44JTbkXwxOgiIb9S-Q9PKSoz_kY8Su-ZCxuDpH5kt1Sx')

def recordSound():


    fs = 44100  # Sample rate
    seconds = 3  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished

    wavio.write("output.wav", myrecording, fs, sampwidth=3) # Save as WAV file 

    recognizer = sr.Recognizer()
    audioFile = sr.AudioFile('./output.wav')
    with audioFile as source:
        data = recognizer.record(source)
    transcript = recognizer.recognize_google(data, key=None)
    # transcript = ""
    # try:
    # transcript = recognizer.recognize_ibm(data, key="44JTbkXwxOgiIb9S-Q9PKSoz_kY8Su-ZCxuDpH5kt1Sx")
    # transcript = recognizer.recognize_ibm(data, username="apikey", password="44JTbkXwxOgiIb9S-Q9PKSoz_kY8Su-ZCxuDpH5kt1Sx")
    # except:
    #     print("Error with transcription try again")

    return transcript


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        if "transcribe" in request.form:
            print("Form Data Received")

            if "file" not in request.files:
                return redirect(request.url)
            
            file = request.files["file"]
            if file.filename == "":
                return redirect(request.url)
            
            if file:
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile(file)
                with audioFile as source:
                    data = recognizer.record(source)
                transcript = recognizer.recognize_google(data, key=None)
                print(transcript)
        elif "record" in request.form:
            transcript = recordSound()



    return render_template('index.html', transcript=transcript)

if __name__=="__main__":
    app.run(debug=True, threaded=True)