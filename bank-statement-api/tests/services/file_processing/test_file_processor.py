import os
from pathlib import Path

from src.app.services.file_processing.file_processor import FileProcessor

# Get the path to the test resources directory
TEST_RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"


class TestFileProcessor:
    def test_process_file(self):
        test_file_path = os.path.join(TEST_RESOURCES_DIR, "Revolut.csv")
        file_content = open(test_file_path, "rb").read()
        file_processor = FileProcessor()
        df = file_processor.process_file(file_content, test_file_path)
        print(df.head())
