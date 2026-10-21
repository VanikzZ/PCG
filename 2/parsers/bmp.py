from .base import (read_exact, u16le, u32le, i32le, CorruptedFile)
from core.models import ImageInfo

BI_RGB, BI_RLE8, BI_RLE4, BI_BITFIELDS, BI_JPEG, BI_PNG = 0, 1, 2, 3, 4, 5
BI_NAMES = {
    0: "BI_RGB (без сжатия)",
    1: "BI_RLE8 (RLE, 8 бит)",
    2: "BI_RLE4 (RLE, 4 бита)",
    3: "BI_BITFIELDS (маски)",
    4: "BI_JPEG",
    5: "BI_PNG",
}


def parse(f, info: ImageInfo, file_size: int):
    magic = read_exact(f, 2)
    if magic != b"BM":
        raise CorruptedFile("Нет сигнатуры 'BM'")
    bf_size = u32le(f)
    _reserved = read_exact(f, 4)
    bf_off_bits = u32le(f)

    bi_size = u32le(f)
    if bi_size < 12:
        raise CorruptedFile(f"Некорректный biSize={bi_size}")
    bi_width = i32le(f)
    bi_height = i32le(f)
    bi_planes = u16le(f)
    bi_bitcount = u16le(f)
    bi_compression = u32le(f)
    bi_size_image = u32le(f)
    bi_xppm = i32le(f)
    bi_yppm = i32le(f)
    bi_clrused = u32le(f)

    if bi_size > 40:
        read_exact(f, bi_size - 40)

    if bf_size and bf_size > file_size:
        raise CorruptedFile(
            f"Размер в заголовке ({bf_size}) > размера файла ({file_size})"
        )
    if bf_off_bits > file_size:
        raise CorruptedFile("bfOffBits указывает за пределы файла")
    if bi_width <= 0:
        raise CorruptedFile("Ширина <= 0")

    info.width = bi_width
    info.height = abs(bi_height)
    info.bit_depth = bi_bitcount
    info.compression = BI_NAMES.get(bi_compression, f"неизвестно ({bi_compression})")
    if bi_xppm:
        info.dpi_x = round(bi_xppm * 0.0254, 2)
    if bi_yppm:
        info.dpi_y = round(bi_yppm * 0.0254, 2)

    if bi_bitcount <= 8:
        palette_colors = bi_clrused or (1 << bi_bitcount)
        info.color_type = f"Palette ({palette_colors} цветов)"
        info.extra["palette"] = palette_colors
    elif bi_bitcount == 24:
        info.color_type = "RGB (TrueColor)"
    elif bi_bitcount == 32:
        info.color_type = "RGBA / RGBX"
    else:
        info.color_type = f"{bi_bitcount} бит"
    info.extra["top_down"] = bi_height < 0