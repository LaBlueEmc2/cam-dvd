import hashlib
import os

class HashService:
    @staticmethod
    def hash_folder(path):
        sha = hashlib.sha256()
        for root, _, files in os.walk(path):
            for f in files:
                with open(os.path.join(root, f), "rb") as fd:
                    sha.update(fd.read())
        return sha.hexdigest()
