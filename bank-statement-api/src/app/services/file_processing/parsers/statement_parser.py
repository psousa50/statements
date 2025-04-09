from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd


class StatementParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse the file and return a pandas DataFrame.

        Args:
            file_path: Path to the file to parse

        Returns:
            pandas DataFrame containing the file data
        """
        pass
