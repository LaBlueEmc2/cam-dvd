import shutil
from services.hash_service import HashService
from services.log_service import LogService

class CopyService:
    @staticmethod
    def copy(src, dst):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        h = HashService.hash_folder(dst)
        LogService.write("COPY", src, dst, h)
