from flask import Flask, render_template, request, redirect

import sounddevice as sd

import wavio
import whisper


app = Flask(__name__)

def recordSound():

    fs = 44100  # Sample rate
    seconds = 10  # Duration of recording

    print('start recording')
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    print('end recording')

    wavio.write("output.wav", myrecording, fs, sampwidth=3) # Save as WAV file 

    transcript = "no text"
    model = whisper.load_model("base")
    result = model.transcribe("output.wav", fp16=False, word_timestamps=True)

    ideal_seconds_per_word = 60 / 115 # 115 wpm

    unclear_words = []
    hesitation_words = []
    pause_timestamps = []
    
    last_word = None
    for segment in result["segments"]:
        for cur_word in segment['words']:
            print(cur_word)
            if cur_word['probability'] < 0.7:
                unclear_words.append((cur_word['word'], cur_word['probability']))
            if cur_word['end'] - cur_word['start'] > ideal_seconds_per_word:
                hesitation_words.append((cur_word['word'], cur_word['end'] - cur_word['start']))
            
            if last_word and cur_word['start'] - last_word['end'] > 0:
                pause_timestamps.append((last_word['end'], cur_word['start']))
        
        last_word = cur_word
    print("Unclear Words:", unclear_words)
    print("Hesitation Words:", hesitation_words)
    print("Pause Timestamps:", pause_timestamps)


    unclear = str(unclear_words).strip('[]')

    hesitation = str(hesitation_words).strip('[]')

    pause =  str(pause_timestamps).strip('[]')

    transcript = result["text"]
    

    return transcript, unclear, hesitation, pause

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    unclear = ""
    hesitation = ""
    pause = ""
    if request.method == "POST":
        if "transcribe" in request.form:
            print("Form Data Received")

            if "file" not in request.files:
                return redirect(request.url)
            
            file = request.files["file"]
            if file.filename == "":
                return redirect(request.url)
            
            if file:
                pass
        elif "record" in request.form:
            transcript, unclear, hesitation, pause = recordSound()

    return render_template('index.html', transcript=transcript, unclear=unclear, hesitation=hesitation, pause=pause)

if __name__=="__main__":
    app.run(debug=True, threaded=True)