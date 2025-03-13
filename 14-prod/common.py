import subprocess

def get_previous_files():
    return subprocess.run(["ls", "batch"], capture_output=True, check=True.stdout.decode("utf-8").strip().split()
