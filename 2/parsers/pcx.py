from .base import read_exact, u16le, CorruptedFile
from core.models import ImageInfo

ENCODINGS = {0: "без сжатия", 1: "RLE (PCX)"}
PALETTE_16 = "EGA/VGA 16-цветовая"


def parse(f, info: ImageInfo, file_size: int):
    f.seek(0)
    manufacturer = read_exact(f, 1)[0]
    if manufacturer != 0x0A:
        raise CorruptedFile("Нет PCX manufacturer = 0x0A")

    version = read_exact(f, 1)[0]
    encoding = read_exact(f, 1)[0]
    bits_per_pixel = read_exact(f, 1)[0]

    xmin = u16le(f)
    ymin = u16le(f)
    xmax = u16le(f)
    ymax = u16le(f)
    hdpi = u16le(f)
    vdpi = u16le(f)
    palette16 = read_exact(f, 48)
    _reserved = read_exact(f, 1)
    nplanes = read_exact(f, 1)[0]
    bytes_per_line = u16le(f)
    palette_info = u16le(f)
    _h_screen = u16le(f)
    _v_screen = u16le(f)

    if xmax < xmin or ymax < ymin:
        raise CorruptedFile("Некорректные границы изображения")

    info.width = xmax - xmin + 1
    info.height = ymax - ymin + 1
    info.dpi_x = float(hdpi)
    info.dpi_y = float(vdpi)
    info.bit_depth = bits_per_pixel * nplanes
    info.compression = ENCODINGS.get(encoding, f"unknown({encoding})")
    info.extra["bytes_per_line"] = bytes_per_line
    info.extra["planes"] = nplanes

    if nplanes == 3 and bits_per_pixel == 8:
        info.color_type = "RGB (TrueColor)"
    elif nplanes == 1 and bits_per_pixel == 8:
        info.color_type = "Palette (256 цветов)"
    elif bits_per_pixel == 1:
        info.color_type = "Monochrome"
    else:
        info.color_type = f"{nplanes} plane(s), {bits_per_pixel} bpp"

    header_size = 128
    if header_size >= file_size:
        raise CorruptedFile("Файл меньше PCX-заголовка")

    if file_size <= header_size:
        raise CorruptedFile("Нет данных после заголовка")