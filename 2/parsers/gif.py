from .base import read_exact, u16le, u8, CorruptedFile
from core.models import ImageInfo


def parse(f, info: ImageInfo, file_size: int):
    sig = read_exact(f, 6)
    if sig not in (b"GIF87a", b"GIF89a"):
        raise CorruptedFile("Нет сигнатуры GIF87a/GIF89a")
    info.extra["version"] = sig.decode()

    w = u16le(f)
    h = u16le(f)
    packed = u8(f)
    _bg = u8(f)
    _aspect = u8(f)

    info.width, info.height = w, h
    gct_flag = (packed >> 7) & 1
    color_res = ((packed >> 4) & 0x07) + 1
    sort_flag = (packed >> 3) & 1
    gct_size = 2 ** ((packed & 0x07) + 1) if gct_flag else 0

    info.bit_depth = color_res
    info.color_type = f"Palette ({gct_size} цветов)" if gct_flag else "Palette (локальная)"
    info.compression = "LZW (GIF)"

    if gct_flag:
        f.seek(gct_size * 3, 1)
    info.extra["global_palette"] = gct_size
    info.extra["sort_flag"] = bool(sort_flag)

    trailer_found = False
    image_count = 0
    while True:
        b = f.read(1)
        if not b:
            raise CorruptedFile("Файл не содержит trailer 0x3B (обрезан)")
        marker = b[0]
        if marker == 0x3B:
            trailer_found = True
            break
        if marker == 0x21:
            ext_type = u8(f)
            if ext_type == 0xF9:
                read_exact(f, 1)
                read_exact(f, 4)
                read_exact(f, 1)
            elif ext_type == 0xFE:
                _skip_subblocks(f)
            elif ext_type == 0xFF:
                read_exact(f, 1)
                _skip_subblocks(f)
            else:
                _skip_subblocks(f)
            continue
        if marker == 0x2C:
            image_count += 1
            read_exact(f, 9)
            f.seek(-1, 1)
            packed = u8(f)
            lct_flag = (packed >> 7) & 1
            if lct_flag:
                lct_size = 2 ** ((packed & 0x07) + 1)
                f.seek(lct_size * 3, 1)
            read_exact(f, 1)
            _skip_subblocks(f)
            continue
        raise CorruptedFile(f"Неизвестный маркер {marker:02X} в GIF")

    if not trailer_found:
        raise CorruptedFile("Нет trailer 0x3B")
    info.extra["image_frames"] = image_count


def _skip_subblocks(f):
    while True:
        n = u8(f)
        if n == 0:
            return
        read_exact(f, n)