import os
import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import logging
import warnings
import argparse

# === Setup Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/tune_music.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
warnings.filterwarnings("ignore", category=DeprecationWarning)

# === Argument Parsing ===
parser = argparse.ArgumentParser()
parser.add_argument("--voice", required=True, help="Path to voice audio file (WAV)")
parser.add_argument("--music", required=True, help="Path to music audio file (WAV)")
parser.add_argument("--genre", type=str, default="pop", help="Genre for mixing")
args = parser.parse_args()

voice_path = args.voice
music_path = args.music
genre = args.genre.lower()

try:
    # === Load Raw Audio ===
    voice_audio, sr_voice = librosa.load(voice_path, sr=None)
    music_audio, sr_music = librosa.load(music_path, sr=None)

    # === Tempo Detection (optional logging) ===
    tempo_voice, _ = librosa.beat.beat_track(y=voice_audio, sr=sr_voice)
    tempo_music, _ = librosa.beat.beat_track(y=music_audio, sr=sr_music)
    # logger.info(f"Voice tempo: {tempo_voice:.2f} | Music tempo: {tempo_music:.2f}")

    # === Duration Alignment ===
    voice_duration = librosa.get_duration(y=voice_audio, sr=sr_voice)
    music_duration = librosa.get_duration(y=music_audio, sr=sr_music)

    if music_duration > voice_duration:
        music_audio = music_audio[:int(voice_duration * sr_music)]
    else:
        repeat_count = int(np.ceil(voice_duration / music_duration))
        music_audio = np.tile(music_audio, repeat_count)[:int(voice_duration * sr_music)]

    sf.write("music_aligned.wav", music_audio, sr_music)
    sf.write("voice_processed.wav", voice_audio, sr_voice)

    # === Load Segments Using Pydub ===
    voice_seg = AudioSegment.from_file("voice_processed.wav")
    music_seg = AudioSegment.from_file("music_aligned.wav")

    # === Duration Truncation ===
    min_duration = min(len(voice_seg), len(music_seg))
    voice_seg = voice_seg[:min_duration]
    music_seg = music_seg[:min_duration]

    # === Logging Volume Info ===
    # logger.info(f"Voice dBFS: {float(voice_seg.dBFS):.2f} | RMS: {int(voice_seg.rms)}")
    # logger.info(f"Music dBFS: {float(music_seg.dBFS):.2f} | RMS: {int(music_seg.rms)}")
    # === Genre-Based Volume Balance ===
    genre_balance = {
        "pop": 5, "hiphop": 4, "rock": 3, "edm": -2,
        "lofi": 0, "metal": 1, "ambient": -5, "jazz": 2
    }
    target_diff = genre_balance.get(genre, 5)
    current_diff = voice_seg.dBFS - music_seg.dBFS
    gain_adjustment = target_diff - current_diff

    voice_seg += gain_adjustment
    # logger.info(f"Adjusted Voice dBFS: {float(voice_seg.dBFS):.2f} | RMS: {int(voice_seg.rms)}")
    logger.info("Reached0")
    # === Mix and Export Final Audio ===
    final_mix = music_seg.overlay(voice_seg)
    final_wav = "output/final_mix.wav"
    final_mp3 = "static/final_song.mp3"
    os.makedirs("output", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    final_mix.export(final_wav, format="wav")
    final_mix.export(final_mp3, format="mp3")
    logger.info("Reached")
    # === Final Log ===
    # logger.info(f"Final Mix dBFS: {float(final_mix.dBFS):.2f} | RMS: {int(final_mix.rms)}")
    # logger.info(f"Final WAV exported: {final_wav}")
    # logger.info(f"Final MP3 exported: {final_mp3}")

    print(f"Final tuned mix exported: {final_mp3}")

except Exception as e:
    logger.exception("Music tuning failed.")
    print(f"Music tuning failed: {e}")
