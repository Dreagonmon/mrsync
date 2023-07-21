import os

class ConfigNotFoundError(Exception):
    def __init__(self, config) -> None:
        super().__init__(f"Config file '{config}' not exists. (default is mrsync.hjson)")

class EntryNotFoundError(Exception):
    def __init__(self, entry) -> None:
        super().__init__(f"Entry '{entry}' not exists.")

class LocationNotFoundError(Exception):
    def __init__(self, location) -> None:
        super().__init__(f"Location '{location}' not exists.")

class LocationNotEndWithSlashError(Exception):
    def __init__(self, location) -> None:
        super().__init__(f"Location '{location}' not ends with '{os.path.sep}'.")

class ModeNotFoundError(Exception):
    def __init__(self, mode) -> None:
        super().__init__(f"Mode '{mode}' not exists.")
