import psutil

class DeviceService:
    @staticmethod
    def list_devices():
        return [p.device for p in psutil.disk_partitions()]
