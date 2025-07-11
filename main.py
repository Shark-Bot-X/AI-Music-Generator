import subprocess
import os
script1 = ["sound","audiocraft_env","main.py"]
script2 = ["clap","clap_env","main.py"]
script3 = ["tortoise","venv_lyrics","lyrics.py"]

def get_python_path(folder,venv):
    return os.path.join(folder,venv,'Scripts' if os.name == 'nt' else 'bin','python')

def run_script(python_path,script_path,input_data=None):
    results = subprocess.run(
        [python_path,script_path],
        input=input_data,
        capture_output=True,
        text=True
    )
    return results.stdout.strip()

out1 = run_script(get_python_path(*script1[:2]),os.path.join(*script1))

def  get_path(script):
    venv_path = script[:-1]
    script_path = script[:-2] + [script[-1]]
    return get_python_path(*venv_path),os.path.join(*script_path)

python3,path3 = get_path(script3)
print("\n🎤 Enter a music prompt:")
user_prompt = input()
print("✨ Generating lyrics...")
lyrics = run_script(python3, path3, input_data=user_prompt)
print("📝 Lyrics:\n", lyrics)
# python2,path2 = get_path(script2)
# print("\n🔍 Extracting CLAP embedding...")
# embedding_output = run_script(python2, path2, input_data=user_prompt)
# print("📐 CLAP Embedded Output")
python1, path1 = get_path(script1)
print("\n🎶 Generating music from lyrics...")
music_output = run_script(python1, path1, input_data=user_prompt)
print("✅ Music Generated:", music_output)
