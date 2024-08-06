from pymetasploit3.msfrpc import MsfRpcClient


class CustomMsfRpcClient:
    _instance = None

    def __new__(cls, password, host, port, ssl):
        if cls._instance is None:
            cls._instance = super(CustomMsfRpcClient, cls).__new__(cls)
            cls._instance.client = MsfRpcClient(password=password, host=host, port=port, ssl=ssl)
        return cls._instance

    def get_client(self):
        return self.client
