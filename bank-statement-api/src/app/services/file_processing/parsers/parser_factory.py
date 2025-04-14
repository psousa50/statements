from src.app.services.file_processing.file_type_detector import FileType
from src.app.services.file_processing.parsers.statement_parser import StatementParser
from src.app.services.file_processing.parsers.statement_parser_factory import create_parser as create_parser_func


class ParserFactory:
    def create_parser(self, file_type: FileType) -> StatementParser:
        return create_parser_func(file_type)
