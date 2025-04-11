from dataclasses import dataclass
from typing import Dict


@dataclass
class ConversionModel:
    column_map: Dict[str, str]
    header_row: int
    start_row: int
