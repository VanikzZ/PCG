import math


_Xn, _Yn, _Zn = 95.047, 100.0, 108.883

_M = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)
_M_inv = (
    ( 3.2404542, -1.5371385, -0.4985314),
    (-0.9692660,  1.8760108,  0.0415560),
    ( 0.0556434, -0.2040259,  1.0572252),
)

_DELTA = 6.0 / 29.0


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _f(t):
    return t ** (1.0 / 3.0) if t > _DELTA ** 3 else t / (3 * _DELTA ** 2) + 4.0 / 29.0


def _f_inv(t):
    return t ** 3 if t > _DELTA else 3 * _DELTA ** 2 * (t - 4.0 / 29.0)


def hsv_to_xyz(h, s, v):
    h = h % 360.0
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))

    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c
    if   h < 60:  r1, g1, b1 = c, x, 0
    elif h < 120: r1, g1, b1 = x, c, 0
    elif h < 180: r1, g1, b1 = 0, c, x
    elif h < 240: r1, g1, b1 = 0, x, c
    elif h < 300: r1, g1, b1 = x, 0, c
    else:         r1, g1, b1 = c, 0, x
    r = r1 + m
    g = g1 + m
    b = b1 + m

    r = _srgb_to_linear(r)
    g = _srgb_to_linear(g)
    b = _srgb_to_linear(b)

    X = (r * _M[0][0] + g * _M[0][1] + b * _M[0][2]) * 100.0
    Y = (r * _M[1][0] + g * _M[1][1] + b * _M[1][2]) * 100.0
    Z = (r * _M[2][0] + g * _M[2][1] + b * _M[2][2]) * 100.0
    return (X, Y, Z)


def xyz_to_hsv(x, y, z):
    X, Y, Z = x / 100.0, y / 100.0, z / 100.0

    rl = X * _M_inv[0][0] + Y * _M_inv[0][1] + Z * _M_inv[0][2]
    gl = X * _M_inv[1][0] + Y * _M_inv[1][1] + Z * _M_inv[1][2]
    bl = X * _M_inv[2][0] + Y * _M_inv[2][1] + Z * _M_inv[2][2]

    r = _linear_to_srgb(rl)
    g = _linear_to_srgb(gl)
    b = _linear_to_srgb(bl)

    mx = max(r, g, b)
    mn = min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = 60.0 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60.0 * ((b - r) / d + 2)
    else:
        h = 60.0 * ((r - g) / d + 4)
    s = 0.0 if mx == 0 else d / mx
    v = mx
    return (h % 360.0, s, v)


def xyz_to_lab(x, y, z):
    fx = _f(x / _Xn)
    fy = _f(y / _Yn)
    fz = _f(z / _Zn)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return (L, a, b)


def lab_to_xyz(L, a, b):
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    x = _Xn * _f_inv(fx)
    y = _Yn * _f_inv(fy)
    z = _Zn * _f_inv(fz)
    return (x, y, z)


def hsv_to_lab(h, s, v):
    return xyz_to_lab(*hsv_to_xyz(h, s, v))


def lab_to_hsv(L, a, b):
    return xyz_to_hsv(*lab_to_xyz(L, a, b))


def hsv_to_rgb255(h, s, v):
    x, y, z = hsv_to_xyz(h, s, v)
    X, Y, Z = x / 100.0, y / 100.0, z / 100.0
    rl = X * _M_inv[0][0] + Y * _M_inv[0][1] + Z * _M_inv[0][2]
    gl = X * _M_inv[1][0] + Y * _M_inv[1][1] + Z * _M_inv[1][2]
    bl = X * _M_inv[2][0] + Y * _M_inv[2][1] + Z * _M_inv[2][2]
    return (
        int(round(max(0.0, min(1.0, _linear_to_srgb(rl))) * 255)),
        int(round(max(0.0, min(1.0, _linear_to_srgb(gl))) * 255)),
        int(round(max(0.0, min(1.0, _linear_to_srgb(bl))) * 255)),
    )