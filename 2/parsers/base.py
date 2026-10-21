import struct


class CorruptedFile(Exception): pass


def read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise CorruptedFile(f"Ожидалось {n} байт, получено {len(data)}")
    return data


def u8(f):  return struct.unpack(">B", read_exact(f, 1))[0]
def u16be(f): return struct.unpack(">H", read_exact(f, 2))[0]
def u16le(f): return struct.unpack("<H", read_exact(f, 2))[0]
def u32be(f): return struct.unpack(">I", read_exact(f, 4))[0]
def u32le(f): return struct.unpack("<I", read_exact(f, 4))[0]
def i32le(f): return struct.unpack("<i", read_exact(f, 4))[0]


def ppm_to_dpi(ppm: int) -> float:
    return round(ppm * 0.0254, 2)