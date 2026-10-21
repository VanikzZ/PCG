from .base import read_exact, u16le, u32le, CorruptedFile
from core.models import ImageInfo

FIELD_TYPES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8,
               11: 4, 12: 8}
T_IMAGE_WIDTH = 256
T_IMAGE_LENGTH = 257
T_BITS_PER_SAMPLE = 258
T_COMPRESSION = 259
T_PHOTOMETRIC = 262
T_XRES = 282
T_YRES = 283
T_RES_UNIT = 296
T_COMPRESSION_NAMES = {
    1: "None", 2: "CCITT 1D", 3: "Group 3 Fax", 4: "Group 4 Fax",
    5: "LZW", 6: "JPEG (old)", 7: "JPEG", 8: "Deflate", 32773: "PackBits",
}
PHOTOMETRIC = {
    0: "WhiteIsZero", 1: "BlackIsZero", 2: "RGB", 3: "Palette",
    4: "Transparency Mask", 5: "CMYK", 6: "YCbCr", 8: "CIELab",
}


def parse(f, info: ImageInfo, file_size: int):
    f.seek(0)
    order = read_exact(f, 2)
    if order == b"II":
        endian = "<"
    elif order == b"MM":
        endian = ">"
    else:
        raise CorruptedFile("Нет TIFF-сигнатуры (II/MM)")

    magic = int.from_bytes(read_exact(f, 2), "little" if endian == "<" else "big")
    if magic != 42:
        raise CorruptedFile(f"Некорректный TIFF-magic {magic}")

    ifd_offset = int.from_bytes(read_exact(f, 4),
                                "little" if endian == "<" else "big")
    if ifd_offset == 0 or ifd_offset >= file_size:
        raise CorruptedFile("Некорректное смещение IFD")

    f.seek(ifd_offset)
    num_entries = int.from_bytes(read_exact(f, 2),
                                 "little" if endian == "<" else "big")
    if num_entries == 0 or num_entries > 4096:
        raise CorruptedFile(f"Подозрительное число записей IFD: {num_entries}")

    fields = {}
    for _ in range(num_entries):
        entry = read_exact(f, 12)
        tag = int.from_bytes(entry[0:2], "little" if endian == "<" else "big")
        ftype = int.from_bytes(entry[2:4], "little" if endian == "<" else "big")
        count = int.from_bytes(entry[4:8], "little" if endian == "<" else "big")
        val_bytes = entry[8:12]
        size = FIELD_TYPES.get(ftype, 1) * count
        if size <= 4:
            raw = val_bytes[:size]
        else:
            off = int.from_bytes(val_bytes, "little" if endian == "<" else "big")
            if off + size > file_size:
                raise CorruptedFile(f"Смещение поля {tag} за пределами файла")
            save = f.tell()
            f.seek(off)
            raw = read_exact(f, size)
            f.seek(save)
        fields[tag] = (ftype, count, raw, endian)

    def get_int(tag):
        if tag not in fields:
            return None
        ftype, count, raw, en = fields[tag]
        if ftype == 3:
            return int.from_bytes(raw[:2], "little" if en == "<" else "big")
        if ftype == 4:
            return int.from_bytes(raw[:4], "little" if en == "<" else "big")
        return None

    def get_rational(tag):
        if tag not in fields:
            return None
        ftype, count, raw, en = fields[tag]
        if ftype == 5 and len(raw) >= 8:
            num = int.from_bytes(raw[0:4], "little" if en == "<" else "big")
            den = int.from_bytes(raw[4:8], "little" if en == "<" else "big")
            if den == 0:
                return None
            return num / den
        return None

    info.width = get_int(T_IMAGE_WIDTH)
    info.height = get_int(T_IMAGE_LENGTH)

    bps = fields.get(T_BITS_PER_SAMPLE)
    if bps:
        ftype, count, raw, en = bps
        samples = count
        bits = int.from_bytes(raw[:2], "little" if en == "<" else "big")
        info.bit_depth = bits * samples if samples > 1 else bits
    else:
        info.bit_depth = None

    comp = get_int(T_COMPRESSION)
    info.compression = T_COMPRESSION_NAMES.get(comp, f"unknown({comp})")

    photo = get_int(T_PHOTOMETRIC)
    info.color_type = PHOTOMETRIC.get(photo, "?")

    xres = get_rational(T_XRES)
    yres = get_rational(T_YRES)
    unit = get_int(T_RES_UNIT)
    if xres is not None:
        info.dpi_x = round(xres, 2) if unit in (None, 2) else round(xres * 2.54, 2)
    if yres is not None:
        info.dpi_y = round(yres, 2) if unit in (None, 2) else round(yres * 2.54, 2)

    if info.width is None or info.height is None:
        raise CorruptedFile("В IFD отсутствуют теги размеров")