DEVICE_STATUS = {
    0: "Inativo",
    1: "Ativo",
    2: "Desconhecido",
}

class Device:
    def __init__(self, id, hostname, ip, device_type, interval, timeout, site, status, last_change):
        self.id = id
        self.hostname = hostname
        self.ip = ip
        self.type = device_type
        self.interval = interval
        self.timeout = timeout
        self.site = site
        self.status = status
        self.last_change = last_change

    def __repr__(self):
        return f"Device({self.id}, {self.hostname}, {self.ip}, {self.tipo}, {self.interval}, {self.timeout}, {self.site}, {self.status}, {self.last_change})"