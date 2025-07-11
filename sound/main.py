import torch
import os
import numpy as np
import logging
from audiocraft.models import MusicGen
from scipy.io.wavfile import write

# === Setup Logging ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/music_generation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

try:
    logger.info("Initializing MusicGen model (facebook/musicgen-small)...")
    musicgen = MusicGen.get_pretrained('facebook/musicgen-small')

    logger.info("Setting generation parameters: duration=21")
    musicgen.set_generation_params(duration=21)

    import sys
    text_prompt = sys.stdin.read().strip()
    if not text_prompt:
        logger.warning("No text prompt provided via stdin. Exiting.")
        print("No prompt entered. Exiting.")
        exit(1)

    logger.info(f"Generating music for prompt: {text_prompt}")
    waveform = musicgen.generate([text_prompt], progress=True)
    audio = waveform[0].cpu().numpy()
    sample_rate = musicgen.sample_rate

    if audio.ndim == 2:
        audio = audio.T

    audio_int16 = np.int16(np.clip(audio, -1, 1) * 32767)

    output_path = "output/music.wav"
    os.makedirs("output", exist_ok=True)
    write(output_path, sample_rate, audio_int16)

    logger.info(f"Music generated and saved at: {output_path}")
    print(f"Music saved at: {output_path}")

except Exception as e:
    logger.exception("Music generation failed.")
    print(f"Music generation failed: {e}")
