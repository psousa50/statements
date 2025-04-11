import logging
import os
import uuid
from datetime import datetime


class DynamicContentFileHandler(logging.Handler):
    def __init__(self, directory="logs/files"):
        super().__init__()
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def emit(self, record):
        try:
            prefix = getattr(record, "prefix", "log")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uid = uuid.uuid4().hex[:8]
            filename = f"{prefix}_{timestamp}_{uid}.log"
            filepath = os.path.join(self.directory, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.format(record))
        except Exception:
            self.handleError(record)
