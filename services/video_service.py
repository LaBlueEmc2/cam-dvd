import subprocess

class VideoService:
    @staticmethod
    def cut(inp, start, end, out):
        subprocess.run([
            "ffmpeg", "-ss", start, "-to", end,
            "-i", inp, "-c", "copy", out
        ], check=True)
