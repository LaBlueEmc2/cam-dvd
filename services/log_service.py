import json
from datetime import datetime

class LogService:
    @staticmethod
    def write(action, src, dst, hashv):
        log = {
            "time": datetime.now().isoformat(),
            "action": action,
            "source": src,
            "target": dst,
            "hash": hashv
        }
        with open("data/logs/log.json", "a") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
