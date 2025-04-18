import logging
import os
import uuid
from datetime import datetime


class DynamicContentFileHandler(logging.Handler):
    def __init__(self, directory="logs/files"):
        super().__init__()
        self.directory = directory

    def emit(self, record):
        try:
            os.makedirs(self.directory, exist_ok=True)
            prefix = getattr(record, "prefix", "log")
            ext = getattr(record, "ext", "log")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
            uid = uuid.uuid4().hex[:8]
            filename = f"{timestamp}_{prefix}_{uid}.{ext}"
            filepath = os.path.join(self.directory, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.format(record))
        except Exception:
            self.handleError(record)
