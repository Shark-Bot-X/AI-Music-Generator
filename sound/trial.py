import torch
import google.generativeai as genai
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import os

# Step 1: Configure Gemini
genai.configure(api_key="AIzaSyCAo1b7pZFAx57qeOULGD_flF3WATGn0s8")  # Replace with your Gemini API key

# Step 2: Generate music prompt from lyrics using Gemini
def get_music_prompt_from_lyrics(lyrics: str) -> str:
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    
    prompt = f"""
You are assisting in creating input for an AI music generation model like **MusicGen**.

Given the lyrics below, perform the following:
1. Create a vivid and musically rich prompt that describes the **genre, instrumentation, emotional tone, and overall atmosphere** suitable for the lyrics.
2. Provide **precise timing directions** for **only the first 10 seconds** of background music. These should describe how the music should evolve — e.g., when to swell, pause, shift instruments, or emphasize lyrics.

Structure your response exactly like this:
---
**Music Prompt:**
<descriptive music style, mood, instruments, genre, tone>

**Timing Instructions:**
0s–2s: <describe intro section and instrument/sound mood>

2s–4s: <describe what happens when the first key lyric line starts>

4s–5s: <describe any musical pause or emphasis>

5s–8s: <describe build-up or instrumentation peak>

8s–10s: <describe how to end the 10s segment with emotion or impact>
---

Lyrics:
{lyrics}
"""
    
    response = model.generate_content(prompt)
    return response.text.strip()

# Step 3: Generate background music using MusicGen
def generate_music(prompt, output_name="generated_music"):
    musicgen = MusicGen.get_pretrained('facebook/musicgen-small')
    musicgen.set_generation_params(duration=10)  # seconds
    waveform = musicgen.generate([prompt])
    audio_write(output_name, waveform[0].cpu(), musicgen.sample_rate, strategy="loudness", format="wav")
    print(f"✅ Music saved as '{output_name}.wav'")

# Step 4: Main logic
def main():
    lyrics = """
        Heartbeat pulsing, a synthetic dawn, <br>
        (Audio Break)
        A thousand whispers, then a siren's call,<br>
        (Audio Break)
        Lost in the rhythm, surrendering all,<br>
        (Audio Break)
        Euphoria's echo, a hypnotic thrall. <br>
        (Audio Break)
        Dancing shadows, where the bright lights fall.
    """

    print("🧠 Generating music prompt with Gemini...")
    music_prompt = get_music_prompt_from_lyrics(lyrics)
    print("🎼 Music Prompt:\n", music_prompt)

    print("🎧 Generating background music with MusicGen...")
    generate_music(music_prompt)

if __name__ == "__main__":
    main()
