def hsv_to_rgb(h, s, v):
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
    return ((r1 + m) * 255, (g1 + m) * 255, (b1 + m) * 255)


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = 60 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60 * ((b - r) / d + 2)
    else:
        h = 60 * ((r - g) / d + 4)
    s = 0.0 if mx == 0 else d / mx
    v = mx
    return (h % 360.0, s, v)


def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


def rgb_to_xyz(r, g, b):
    rl, gl, bl = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    x = rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041
    return (x * 100.0, y * 100.0, z * 100.0)  # часто в 0..100


def xyz_to_rgb(x, y, z):
    x, y, z = x / 100.0, y / 100.0, z / 100.0
    rl =  x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    gl =  x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    bl =  x * 0.0556434 + y * -0.2040259 + z * 1.0572252
    return (_linear_to_srgb(rl), _linear_to_srgb(gl), _linear_to_srgb(bl))


_Xn, _Yn, _Zn = 95.047, 100.0, 108.883


def _f(t):
    delta = 6 / 29
    return t ** (1 / 3) if t > delta ** 3 else t / (3 * delta ** 2) + 4 / 29


def _f_inv(t):
    delta = 6 / 29
    return t ** 3 if t > delta else 3 * delta ** 2 * (t - 4 / 29)


def xyz_to_lab(x, y, z):
    fx = _f(x / _Xn)
    fy = _f(y / _Yn)
    fz = _f(z / _Zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return (L, a, b)


def lab_to_xyz(L, a, b):
    fy = (L + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200
    x = _Xn * _f_inv(fx)
    y = _Yn * _f_inv(fy)
    z = _Zn * _f_inv(fz)
    return (x, y, z)


def hsv_to_xyz(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    return rgb_to_xyz(r, g, b)


def xyz_to_hsv(x, y, z):
    r, g, b = xyz_to_rgb(x, y, z)
    return rgb_to_hsv(r, g, b)


def hsv_to_lab(h, s, v):
    return xyz_to_lab(*hsv_to_xyz(h, s, v))


def lab_to_hsv(L, a, b):
    return xyz_to_hsv(*lab_to_xyz(L, a, b))


def lab_to_xyz_public(L, a, b):
    return lab_to_xyz(L, a, b)


def xyz_to_lab_public(x, y, z):
    return xyz_to_lab(x, y, z)


def hsv_to_rgb_public(h, s, v):
    return hsv_to_rgb(h, s, v)


def rgb_to_hsv_public(r, g, b):
    return rgb_to_hsv(r, g, b)