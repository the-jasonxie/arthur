import sounddevice as sd
import numpy as np
import wave
import subprocess
import os

def run_stt():
    # Settings
    duration = 5
    samplerate = 16000  
    filename = "output.wav"

    print("Recording...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("Done recording!")

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)  # 16 bits = 2 bytes
        f.setframerate(samplerate)
        f.writeframes(recording.tobytes())

    print(f"Saved to {filename}")

    # whisper.cpp error check
    whisper_model_path = "../whisper.cpp/models/ggml-base.en.bin"
    if not os.path.exists(whisper_model_path):
        print(f"Error: Whisper model not found at {whisper_model_path}")
        exit(1)

    # Run whisper.cpp transcription command
    whisper_command = f"../whisper.cpp/build/bin/whisper-cli -m {whisper_model_path} -f {filename}"
    print(f"Running command: {whisper_command}")

    try:
        transcription = subprocess.run(whisper_command, shell=True, capture_output=True, text=True, check=True)
        print(f"Transcription: {transcription.stdout}")
        return transcription.stdout.strip() #returns string instead of entire subprocess and strips spaces/newlines
    except subprocess.CalledProcessError as e:
        print(f"Error during transcription: {e}")
        print(f"stderr: {e.stderr}")
        return ""

    

    
