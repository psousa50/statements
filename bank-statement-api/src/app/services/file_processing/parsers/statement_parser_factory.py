from src.app.services.file_processing.file_type_detector import FileType
from src.app.services.file_processing.parsers.csv_parser import CSVParser
from src.app.services.file_processing.parsers.excel_parser import ExcelParser
from src.app.services.file_processing.parsers.statement_parser import StatementParser


def create_parser(file_type: FileType) -> StatementParser:
    if file_type == FileType.CSV:
        return CSVParser()
    elif file_type == FileType.EXCEL:
        return ExcelParser()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
