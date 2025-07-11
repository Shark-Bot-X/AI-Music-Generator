import os
import sys
import logging
import warnings
import subprocess
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
os.environ['XFORMERS_MORE_DETAILS'] = '0'
# === Flask Setup ===
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "output"
app.config["ALLOWED_EXTENSIONS"] = {'wav', 'mp3'}

# === Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/music_generation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
warnings.filterwarnings("ignore", category=DeprecationWarning)

# === Constants ===
GENRE_DEFAULT = "pop"
VOICE_SCRIPT = os.path.join("Tortoise", "lyrics.py")
VOICE_VENV = os.path.join("Tortoise", "musicenv")
MUSIC_SCRIPT = os.path.join("sound", "main.py")
MUSIC_VENV = os.path.join("sound", "audiocraft_env")
VOICE_PATH = os.path.join("output", "voice.wav")
MUSIC_PATH = os.path.join("output", "music.wav")
FINAL_MP3_PATH = "static/final_song.mp3"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def get_python_path(venv_path):
    return os.path.join(venv_path, 'Scripts' if os.name == 'nt' else 'bin', 'python')

def run_script(python_path, script_path, input_data=None):
    try:
        result = subprocess.run(
            [python_path, script_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=300
        )
        logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.error(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            logger.error(f"Script failed with return code: {result.returncode}")
            return None
        return result.stdout.strip()
    except Exception as e:
        logger.exception(f"Error running {script_path}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        title = request.form.get('title', 'My Song')
        lyrics = request.form.get('lyrics', '')
        genre = request.form.get('genre', GENRE_DEFAULT)
        mood = request.form.get('mood', 'happy')
        use_existing_audio = request.form.get('use_existing_audio') == 'true'

        logger.info(f"Starting generation: {title}, Genre: {genre}, Mood: {mood}, Using audio: {use_existing_audio}")

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        # === Step 1: Handle Uploaded Audio ===
        if use_existing_audio:
            file = request.files.get('audio_file')
            if not file or file.filename == '':
                return Response("Audio file is required", status=400)

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                voice_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(voice_path)
                logger.info(f"Uploaded audio saved to: {voice_path}")
            else:
                return Response(" audio format", status=400)
        else:
            if not lyrics:
                return Response("Lyrics are required", status=400)
            logger.info("Generating voice...")
            voice_output = run_script(get_python_path(VOICE_VENV), VOICE_SCRIPT, input_data=lyrics)
            if not voice_output or not os.path.exists(VOICE_PATH):
                return Response("Voice generation failed", status=500)
            voice_path = VOICE_PATH

        # === Step 2: Generate Music ===
        logger.info("Generating background music...")
        prompt = f"{title} in {genre} style with {mood} mood"
        if lyrics and not use_existing_audio:
            prompt += f" | Lyrics: {lyrics[:100]}..."
        music_output = run_script(get_python_path(MUSIC_VENV), MUSIC_SCRIPT, input_data=prompt)
        if not music_output or not os.path.exists(MUSIC_PATH):
            return Response("Music generation failed", status=500)
        music_path = MUSIC_PATH

        # === Step 3: Run Tuning Script ===
        logger.info("Mixing voice & music using tune_music.py")
        tune_script = os.path.join("tune_music.py")
        result = subprocess.run(
            [sys.executable, tune_script, "--voice", voice_path, "--music", music_path, "--genre", genre],
            capture_output=True,
            text=True
        )
        logger.info("tune_music.py Output:\n" + result.stdout)
        if result.stderr:
            logger.error("tune_music.py Errors:\n" + result.stderr)

        if result.returncode != 0:
            return Response("Final tuning failed", status=500)

        logger.info("Final MP3 available at: " + FINAL_MP3_PATH)
        return render_template("result.html", title=title, audio_file=FINAL_MP3_PATH)

    except Exception as e:
        logger.exception("Error in /generate")
        return Response(f"Internal Error: {e}", status=500)

if __name__ == '__main__':
    app.run(debug=True)
