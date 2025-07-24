class MonitoringData:
    def __init__(
        self,
        timestamp,
        device_id,
        status,
        pack_sent,
        pack_recv,
        rtt_min,
        rtt_max,
        rtt_avg,
    ):
        self.timestamp = timestamp
        self.device_id = device_id
        self.status = status
        self.pack_sent = pack_sent
        self.pack_recv = pack_recv
        self.rtt_min = rtt_min
        self.rtt_max = rtt_max
        self.rtt_avg = rtt_avg

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "device_id": self.device_id,
            "status": self.status,
            "pack_sent": self.pack_sent,
            "pack_recv": self.pack_recv,
            "rtt_min": self.rtt_min,
            "rtt_max": self.rtt_max,
            "rtt_avg": self.rtt_avg,
        }
