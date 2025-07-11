import sounddevice as sd
from scipy.io.wavfile import write

fs = 24000  # Sample rate
seconds = 10  # Duration
print("🎙️ Recording...")
my_audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()
write("voice.wav", fs, my_audio)
print("✅ Saved as sample3.wav")
