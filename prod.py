import subprocess
import shutil
import os


def create_executable(script_path):
    command = f"pyinstaller --onefile {script_path}"
    subprocess.run(command, shell=True)


create_executable("bot_playlists.py")

exe_file = 'dist/bot_playlists.exe'
prod_folder = 'Prod'
prod_file = os.path.join(prod_folder, os.path.basename(exe_file))

shutil.make_archive('Prod', 'zip', prod_folder)

os.makedirs(prod_folder, exist_ok=True)
if os.path.exists(prod_file):
    os.remove(prod_file)
shutil.move(exe_file, prod_file)

if os.path.exists('Prod.zip'):
    os.remove('Prod.zip')

shutil.make_archive('Prod', 'zip', prod_folder)


for folder in ['build', 'dist']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

if os.path.exists('bot_playlists.spec'):
    os.remove('bot_playlists.spec')
