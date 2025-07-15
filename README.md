# 🎶 AI Music Production App

This is a **Flask-based AI music generation system** that creates **vocals from lyrics**, generates **background music**, and blends both into a **final MP3** using a custom audio tuning script.

---

## 🚀 Features

- 🎤 Generate singing voice from lyrics using Bark/Tortoise
- 🎼 Generate background music based on genre, mood, and song title using MusicGen
- 🎚️ Mix both using `tune_music.py` to produce studio-style output
- 🖥️ Web UI for uploading audio or entering lyrics
- 🔁 Option to reuse custom vocal tracks

---

## 🗂️ Project Structure

music_production_app/
├── app.py # Main Flask app
├── templates/ # HTML templates
│ ├── index.html
│ └── result.html
├── static/ # Final output location
│ └── final_song.mp3
├── output/ # Intermediate audio files
├── logs/ # Logging outputs
├── tune_music.py # Mixer script
├── sound/ # MusicGen environment
│ ├── main.py
│ └── audiocraft_env/ # venv for MusicGen
├── Tortoise/ # Voice generation environment
│ ├── lyrics.py
│ └── musicenv/ # venv for Tortoise
├── .gitignore
└── README.md


---

## 🛠️ Setup Instructions

### 1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/music_production_app.git
cd music_production_app
2. Set Up Virtual Environments

🐢 Tortoise (for voice generation)
cd Tortoise
python -m venv musicenv
# Activate:
# Windows: musicenv\Scripts\activate
# Linux/macOS: source musicenv/bin/activate

Install dependencies:
pip install torch==2.0.1
pip install transformers==4.35.0
pip install tokenizers==0.14.0

# Clone Tortoise repo (custom)
git clone https://github.com/neonbjb/tortoise-tts.git
cd tortoise-tts
# ⚠️ Remove or comment out this line in setup.cfg before installing:
# torchaudio==2.0.2
python setup.py install

🎵 Audiocraft (for music generation)
cd ../../sound
python -m venv audiocraft_env
# Activate:
# Windows: audiocraft_env\Scripts\activate
# Linux/macOS: source audiocraft_env/bin/activate

Install dependencies:
pip install torch==2.1.0
pip install "transformers>=4.31.0"
# Plus any additional requirements for MusicGen
3. Run the Flask App
Back to root:
cd ..
python app.py
Access via browser: http://127.0.0.1:5000

🧪 How It Works
User inputs:
Song title
Lyrics or voice upload
Genre and mood
Flask backend:
Uses Tortoise (Tortoise/lyrics.py) to synthesize singing
Uses MusicGen (sound/main.py) to generate background music
Combines both with tune_music.py
Final MP3 is stored at static/final_song.mp3 and played on result page

✅ Requirements
Python 3.9+
Flask
FFmpeg
Separate virtual environments:
Tortoise: torch==2.0.1, transformers==4.35.0, tokenizers==0.14.0
MusicGen: torch==2.1.0, transformers>=4.31.0

📁 .gitignore
# Python cache
__pycache__/
*.py[cod]

# Virtual environments
sound/audiocraft_env/
Tortoise/musicenv/

# Logs and output
logs/
output/
static/final_song.mp3


## 🌟 Sample outputs
[🔊 Listen](output/best_final_mix.wav) 

## 🖼️ UI Screenshot
![Alt Text](output/image.png)


🧠 Future Improvements
Docker-based deployment for easy setup
Real-time progress bar during generation
Support for multilingual lyrics
Genre-tuned mixing presets in tune_music.py

📝 License
MIT License © 2025 Sneh
Let me know if you’d like:
Separate requirements.txt for each env
Dockerfile for deployment
Sample data/test mode
