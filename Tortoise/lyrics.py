import torch
import sys
import os
import re
import logging
import torchaudio
from transformers import pipeline
import google.generativeai as genai
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice, load_audio

# --- Setup Logging ---
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/music_generation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# --- Voice Styles ---
VOICE_MAP = {
    "rock": "snakes",
    "pop": "emma",
    "jazz": "train_dreams",
    "classical": "freeman",
    "metal": "tom",
    "hip-hop": "denerio",
    "soul": "applejack",
    "vintage": "train_daws",
    "edm": "train_atkins"
}

USE_GEMINI = True
GEMINI_API_KEY = "AIzaSyCZWwW3SW3J940x5GOR4CP0goM6_9ZLRVI"
OUTPUT_VOICE = "output/voice.wav"

# --- Setup Gemini ---
if USE_GEMINI:
    logger.info("Configuring Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")
    logger.info("Gemini model loaded.")

tts = TextToSpeech()

def detect_voice(prompt: str) -> str:
    genre_list = ", ".join(VOICE_MAP.keys())
    logger.info("Detecting genre from prompt...")
    response = gemini_model.generate_content(
        f"You are a music assistant. Given this prompt: \"{prompt}\", "
        f"guess the best matching music genre or style from this list: {genre_list}. "
        f"Only respond with one of the listed genres, nothing else."
    )
    genre = response.text.strip().lower()
    logger.info(f"Detected genre: {genre}")
    return VOICE_MAP.get(genre, "denerio")

def generate_lyrics(music_prompt: str) -> str:
    logger.info("Generating lyrics from prompt...")
    response = gemini_model.generate_content(
        f"""
Generate poetic song lyrics based on the following music description. 
The lyrics should reflect the mood, instruments, and energy described.

Guidelines:
- Output exactly 4 to 6 lines.
- Make them emotionally expressive and rhythmically suitable for syncing with music.
- Avoid any labels like 'Lyrics:', 'Music:', etc.
- Do not use brackets or parentheses.
- Do not include 'audio break' or similar phrases.
- Keep it clean, focused, and evocative.

Music Prompt:
\"\"\"{music_prompt}\"\"\"
"""
    )
    lyrics = response.text.strip()
    logger.info("Lyrics generated successfully.")
    for ending in ["music", "Music", "MUSIC"]:
        if lyrics.lower().endswith(ending):
            lyrics = lyrics[:-(len(ending))].strip()
    return lyrics

def split_text(text, max_len=300):
    sentences = re.split(r'(?<=[.!?\n])', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) > max_len:
            chunks.append(current.strip())
            current = sentence
        else:
            current += sentence
    if current:
        chunks.append(current.strip())
    return chunks

def generate_voice(lyrics: str, filename: str, voice_name: str) -> None:
    logger.info(f"Generating voice using '{voice_name}'...")
    chunks = split_text(lyrics)
    combined_audio = []

    logger.info("Loading voice model...")
    voice_samples, conditioning_latents = load_voice(voice_name)

    for i, chunk in enumerate(chunks):
        logger.info(f"Synthesizing chunk {i+1}/{len(chunks)}...")
        audio = tts.tts_with_preset(
            chunk,
            voice_samples=voice_samples,
            conditioning_latents=conditioning_latents,
            preset="ultra_fast"
        )
        combined_audio.append(audio)

    full_audio = torch.cat(combined_audio, dim=-1)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    torchaudio.save(filename, full_audio.squeeze(0).cpu(), 24000)
    logger.info(f"Voice saved to {filename}")

# --- Main Entry ---
def main():
    if not sys.stdin.isatty():
        user_input = sys.stdin.read().strip()
    else:
        print("Enter a music prompt:")
        user_input = input("> ")

    logger.info("Starting generation pipeline.")
    logger.info(f"User Prompt: {user_input}")

    lyrics = generate_lyrics(user_input)
    logger.info(f"Generated Lyrics:\n{lyrics}")

    selected_voice = detect_voice(user_input)
    logger.info(f"Selected Voice: {selected_voice}")

    generate_voice(lyrics, OUTPUT_VOICE, selected_voice)

    logger.info("All steps complete.")

if __name__ == "__main__":
    main()
