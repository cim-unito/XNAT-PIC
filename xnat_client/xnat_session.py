import xnat

class XnatSession:
    def __init__(self, address: str, username: str, password: str):
        self.address = address.rstrip("/")
        self.username = username
        self.password = password
        self._session = None

    def connect(self) -> bool:
        try:
            self._session = xnat.connect(self.address, self.username, self.password)
            return True
        except Exception as e:
            print("XNAT connection error:", e)
            self._session = None
            return False

    def disconnect(self):
        if self._session:
            try:
                self._session.disconnect()
            except:
                pass

        self._session = None

    @property
    def session(self):
        return self._session

