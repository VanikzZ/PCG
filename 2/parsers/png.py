import zlib
from .base import read_exact, u32be, u8, ppm_to_dpi, CorruptedFile
from core.models import ImageInfo

PNG_SIG = b"\x89PNG\r\n\x1a\n"

COLOR_TYPES = {
    0: "Grayscale",
    2: "RGB",
    3: "Palette",
    4: "Grayscale + Alpha",
    6: "RGBA",
}
COMPRESSION = {0: "Deflate (zlib)"}


def parse(f, info: ImageInfo, file_size: int):
    sig = read_exact(f, 8)
    if sig != PNG_SIG:
        raise CorruptedFile("Неверная PNG-сигнатура")

    seen_ihdr = seen_iend = False
    idat_count = 0
    palette_count = 0

    while True:
        hdr = f.read(8)
        if len(hdr) == 0:
            break
        if len(hdr) != 8:
            raise CorruptedFile("Обрыв на чтении заголовка чанка")
        length = u32be_from(hdr[:4])
        ctype = hdr[4:8]
        if length > file_size:
            raise CorruptedFile(f"Длина чанка {length} > размер файла")

        if ctype == b"IHDR":
            if length != 13:
                raise CorruptedFile("IHDR неверной длины")
            data = read_exact(f, 13)
            info.width = int.from_bytes(data[0:4], "big")
            info.height = int.from_bytes(data[4:8], "big")
            info.bit_depth = data[8]
            ct = data[9]
            info.color_type = COLOR_TYPES.get(ct, f"unknown({ct})")
            info.compression = COMPRESSION.get(data[10], f"compression({data[10]})")
            seen_ihdr = True
            read_exact(f, 4)
        elif ctype == b"PLTE":
            palette_count = length // 3
            info.extra["palette"] = palette_count
            f.seek(length + 4, 1)
        elif ctype == b"pHYs":
            if length == 9:
                d = read_exact(f, 9)
                xppm = int.from_bytes(d[0:4], "big")
                yppm = int.from_bytes(d[4:8], "big")
                unit = d[8]
                if unit == 1:
                    info.dpi_x = ppm_to_dpi(xppm)
                    info.dpi_y = ppm_to_dpi(yppm)
                f.seek(4, 1)
            else:
                f.seek(length + 4, 1)
        elif ctype == b"IDAT":
            idat_count += 1
            f.seek(length + 4, 1)
        elif ctype == b"IEND":
            seen_iend = True
            break
        else:
            f.seek(length + 4, 1)

    if not seen_ihdr:
        raise CorruptedFile("Отсутствует чанк IHDR")
    if not seen_iend:
        raise CorruptedFile("Отсутствует чанк IEND (файл обрезан)")
    info.extra["idat_chunks"] = idat_count


def u32be_from(b: bytes) -> int:
    return int.from_bytes(b, "big")