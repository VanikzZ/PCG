import os
from . import bmp, png, jpg, gif, tif, pcx
from core.models import ImageInfo

SIGNATURES = {
    b"\xFF\xD8": ("JPEG", jpg),
    b"\x89PNG\r\n\x1a\n": ("PNG", png),
    b"GIF87a": ("GIF", gif),
    b"GIF89a": ("GIF", gif),
    b"BM": ("BMP", bmp),
    b"II*\x00": ("TIFF", tif),
    b"MM\x00*": ("TIFF", tif),
    b"\x0A": ("PCX", pcx)
}


def _detect(head: bytes):
    for sig, entry in SIGNATURES.items():
        if head.startswith(sig):
            return entry
    return None, None


def parse_file(path: str) -> ImageInfo:
    info = ImageInfo(filename=os.path.basename(path))
    try:
        file_size = os.path.getsize(path)
        if file_size < 2:
            raise Exception("Файл слишком мал")

        with open(path, "rb") as f:
            head = f.read(16)
            if not head:
                raise Exception("Пустой файл")
            fmt, module = _detect(head)
            if module is None:
                raise Exception("Неизвестная сигнатура (возможно подмена расширения)")
            info.fmt = fmt
            f.seek(0)
            module.parse(f, info, file_size)

        ext = os.path.splitext(path)[1].lower()
        ext_fmt = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
            ".gif": "GIF", ".bmp": "BMP", ".tif": "TIFF", ".tiff": "TIFF",
            ".pcx": "PCX",
        }.get(ext)
        if ext_fmt and ext_fmt != fmt:
            info.status = "EXT_MISMATCH"
            info.error = f"Расширение {ext}, но содержимое {fmt}"
        else:
            info.status = "OK"

    except Exception as e:
        info.status = "CORRUPTED"
        info.error = str(e)

    return info