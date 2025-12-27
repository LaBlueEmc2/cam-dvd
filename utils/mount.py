import subprocess

def mount_readonly(dev, target):
    subprocess.run(["mount", "-o", "ro", dev, target], check=True)
