from enum import Enum, auto
from pathlib import Path
from typing import Optional


class FileType(Enum):
    CSV = auto()
    EXCEL = auto()
    PDF = auto()
    UNKNOWN = auto()


class FileTypeDetector:
    def detect_file_type(self, file_path: str) -> FileType:
        extension = Path(file_path).suffix.lower().lstrip(".")

        if extension == "csv":
            return FileType.CSV
        elif extension in ["xlsx", "xls"]:
            return FileType.EXCEL
        elif extension == "pdf":
            return FileType.PDF
        else:
            return FileType.UNKNOWN
