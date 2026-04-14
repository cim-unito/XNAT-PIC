class ModelCustomForm:
    def __init__(self):
        self._level = None

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    def reset_level(self):
        self._level = None

    def reset_state(self):
        self.reset_level()

