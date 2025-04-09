from src.app.services.file_processing.file_type_detector import (
    FileType,
    FileTypeDetector,
)


class TestFileProcessor:
    def test_detect_file_type(self):
        # Arrange
        file_processor = FileTypeDetector()

        # Act & Assert
        assert file_processor.detect_file_type("test.csv") == FileType.CSV
        assert file_processor.detect_file_type("test.xlsx") == FileType.EXCEL
        assert file_processor.detect_file_type("test.xls") == FileType.EXCEL
        assert file_processor.detect_file_type("test.pdf") == FileType.PDF
        assert file_processor.detect_file_type("test.unknown") == FileType.UNKNOWN

    def test_detect_file_type_case_insensitive(self):
        # Arrange
        file_processor = FileTypeDetector()

        # Act & Assert
        assert file_processor.detect_file_type("TEST.CSV") == FileType.CSV
        assert file_processor.detect_file_type("Test.Xlsx") == FileType.EXCEL
        assert file_processor.detect_file_type("test.PDF") == FileType.PDF

    def test_detect_file_type_with_path(self):
        # Arrange
        file_processor = FileTypeDetector()

        # Act & Assert
        assert file_processor.detect_file_type("/path/to/test.csv") == FileType.CSV
        assert (
            file_processor.detect_file_type("C:\\Users\\test\\documents\\file.xlsx")
            == FileType.EXCEL
        )
        assert (
            file_processor.detect_file_type("../statements/bank_statement.pdf")
            == FileType.PDF
        )
