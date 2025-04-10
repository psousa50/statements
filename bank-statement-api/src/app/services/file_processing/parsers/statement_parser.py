from abc import ABC, abstractmethod

import pandas as pd


class StatementParser(ABC):
    @abstractmethod
    def parse(self, file_content: bytes) -> pd.DataFrame:
        pass
