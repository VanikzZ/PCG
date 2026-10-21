from .base import read_exact, u16be, u8, CorruptedFile
from core.models import ImageInfo

SOI, EOI = 0xD8, 0xD9
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
COMPONENTS_TYPE = {1: "Grayscale", 3: "YCbCr / RGB", 4: "CMYK / YCCK"}


def parse(f, info: ImageInfo, file_size: int):
    soi = read_exact(f, 2)
    if soi != b"\xFF\xD8":
        raise CorruptedFile("Нет маркера SOI")

    qt_tables = []
    seen_eoi = False
    progress = 2

    while progress < file_size:
        b = f.read(1)
        if not b:
            break
        if b != b"\xFF":
            continue
        marker = f.read(1)
        if not marker:
            break
        m = marker[0]
        if m == 0xFF:
            f.seek(-1, 1)
            continue
        if m == EOI:
            seen_eoi = True
            break
        if 0xD0 <= m <= 0xD7 or m == 0x01:
            continue
        len_bytes = f.read(2)
        if len(len_bytes) != 2:
            raise CorruptedFile("Обрыв на длине сегмента")
        seg_len = int.from_bytes(len_bytes, "big")
        if seg_len < 2:
            raise CorruptedFile(f"Некорректная длина сегмента {seg_len}")
        payload_remaining = seg_len - 2

        if m in SOF_MARKERS:
            if payload_remaining < 6:
                raise CorruptedFile("SOF слишком короткий")
            data = read_exact(f, payload_remaining)
            info.bit_depth = data[0]
            info.height = int.from_bytes(data[1:3], "big")
            info.width = int.from_bytes(data[3:5], "big")
            ncomp = data[5]
            info.color_type = COMPONENTS_TYPE.get(ncomp, f"{ncomp} комп.")
            info.compression = _sof_name(m)
        elif m == 0xDB:
            data = read_exact(f, payload_remaining)
            qt_tables.append(len(data))
            info.extra["quant_tables_bytes"] = qt_tables[:]
        elif m == 0xE0:
            data = read_exact(f, payload_remaining)
            info.extra["jfif"] = data[:5] == b"JFIF\x00"
            if info.extra["jfif"] and len(data) >= 12:
                units = data[7]
                xd = int.from_bytes(data[8:10], "big")
                yd = int.from_bytes(data[10:12], "big")
                if units == 1:
                    info.dpi_x, info.dpi_y = float(xd), float(yd)
                elif units == 2:
                    info.dpi_x = round(xd * 2.54, 2)
                    info.dpi_y = round(yd * 2.54, 2)
        elif m == 0xE1:
            data = read_exact(f, payload_remaining)
            info.extra["exif"] = data[:6] == b"Exif\x00\x00"
        elif m == 0xDA:
            data = read_exact(f, payload_remaining)
            pos = f.tell()
            while pos < file_size:
                chunk = f.read(min(65536, file_size - pos))
                if not chunk:
                    break
                idx = chunk.find(b"\xFF\xD9")
                if idx != -1:
                    seen_eoi = True
                    break
                pos += len(chunk)
            if not seen_eoi:
                raise CorruptedFile("Не найден маркер EOI (FF D9)")
            break
        else:
            f.seek(payload_remaining, 1)

        progress = f.tell()

    if info.width is None or info.height is None:
        raise CorruptedFile("Не найден SOF-сегмент (нет размеров)")
    if not seen_eoi:
        raise CorruptedFile("Не найден маркер EOI (FF D9)")


def _sof_name(m: int) -> str:
    names = {
        0xC0: "Baseline DCT (Huffman)",
        0xC1: "Extended sequential DCT",
        0xC2: "Progressive DCT",
        0xC3: "Lossless",
        0xC5: "Differential sequential",
        0xC6: "Differential progressive",
        0xC7: "Differential lossless",
        0xC9: "Extended sequential (arith)",
        0xCA: "Progressive (arith)",
        0xCB: "Lossless (arith)",
    }
    return names.get(m, "DCT")