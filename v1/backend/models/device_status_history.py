class DeviceStatusHistory:
    def __init__(self, id, device_id, status, last_status_change, count):
        self.id = id
        self.device_id = device_id
        self.status = status
        self.last_status_change = last_status_change
        self.count = count

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "status": self.status,
            "last_status_change": self.last_status_change,
            "count": self.count,
        }
