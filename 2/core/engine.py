import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional

from core.models import ImageInfo
from parsers import parse_file

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp",
                 ".tif", ".tiff", ".pcx"}


class ScanEngine:
    def __init__(self, workers: Optional[int] = None):
        if workers is None:
            cpu = os.cpu_count() or 4
            workers = max(4, min(32, cpu * 2))
        self.workers = workers
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def scan(self, folder: str,
             on_result: Callable[[ImageInfo], None],
             on_progress: Callable[[int, int], None],
             recursive: bool = False):
        files: List[str] = []
        for root, _dirs, names in os.walk(folder):
            for n in names:
                if os.path.splitext(n)[1].lower() in SUPPORTED_EXT:
                    files.append(os.path.join(root, n))
            if not recursive:
                break

        total = len(files)
        done = 0
        on_progress(0, total)

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(parse_file, p): p for p in files}
            for fut in as_completed(futures):
                if self._stop.is_set():
                    pool.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    info = fut.result()
                except Exception as e:
                    p = futures[fut]
                    info = ImageInfo(filename=os.path.basename(p),
                                     status="CORRUPTED", error=str(e))
                done += 1
                on_result(info)
                on_progress(done, total)