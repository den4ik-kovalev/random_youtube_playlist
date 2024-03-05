from pathlib import Path
from typing import Union

import yaml


class YAMLFile:

    def __init__(self, path: Path, auto_create=True) -> None:
        if path.suffix != ".yml":
            raise Exception("The file extension must be .yml")
        self._path = path
        if auto_create and not self.exists():
            self.write(None)

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def read(self) -> Union[dict, list, None]:
        with open(self._path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def write(self, data: Union[dict, list, None]) -> None:
        with open(self._path, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file)
