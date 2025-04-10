from enum import Enum, auto
from pathlib import Path


class FileType(Enum):
    CSV = auto()
    EXCEL = auto()
    PDF = auto()
    UNKNOWN = auto()


class FileTypeDetector:
    def detect_file_type(self, file_name: str) -> FileType:
        extension = Path(file_name).suffix.lower().lstrip(".")
        return self._get_file_type_from_extension(extension)

    def _get_file_type_from_extension(self, extension: str) -> FileType:
        if extension == "csv":
            return FileType.CSV
        elif extension in ["xlsx", "xls"]:
            return FileType.EXCEL
        elif extension == "pdf":
            return FileType.PDF
        else:
            return FileType.UNKNOWN
