import subprocess
from services.log_service import LogService

class BurnService:
    @staticmethod
    def burn(folder):
        subprocess.run(["genisoimage", "-o", "/tmp/data.iso", folder], check=True)
        subprocess.run(["wodim", "/tmp/data.iso"], check=True)
        LogService.write("BURN", folder, "CD/DVD", "")
