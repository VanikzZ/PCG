"""Запуск: python tests.py"""
from model import (
    hsv_to_rgb, rgb_to_hsv,
    rgb_to_xyz, xyz_to_rgb,
    xyz_to_lab, lab_to_xyz,
    hsv_to_lab, lab_to_hsv,
)


def approx(a, b, eps=1e-2):
    return abs(a - b) <= eps


def test_red_hsv_to_lab():
    L, a, b = hsv_to_lab(0, 1, 1)
    assert approx(L, 53.24, 0.5), L
    assert approx(a, 80.09, 0.5), a
    assert approx(b, 67.20, 0.5), b
    print("OK: HSV(0,1,1) -> LAB ≈ (53.24, 80.09, 67.20)")


def test_white_lab():
    L, a, b = hsv_to_lab(0, 0, 1)
    assert approx(L, 100, 0.1), L
    assert approx(a, 0, 0.1), a
    assert approx(b, 0, 0.1), b
    print("OK: белый -> LAB ≈ (100, 0, 0)")


def test_black():
    L, a, b = hsv_to_lab(0, 0, 0)
    assert approx(L, 0, 0.1) and approx(a, 0, 0.1) and approx(b, 0, 0.1)
    print("OK: чёрный -> LAB ≈ (0, 0, 0)")


def test_rgb_xyz_roundtrip():
    for rgb in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 64, 32), (7, 200, 90)]:
        x, y, z = rgb_to_xyz(*rgb)
        r2, g2, b2 = xyz_to_rgb(x, y, z)
        assert approx(r2, rgb[0], 0.5), (rgb, (r2, g2, b2))
        assert approx(g2, rgb[1], 0.5), (rgb, (r2, g2, b2))
        assert approx(b2, rgb[2], 0.5), (rgb, (r2, g2, b2))
    print("OK: RGB -> XYZ -> RGB")


def test_xyz_lab_roundtrip():
    for xyz in [(41.24, 21.26, 1.93), (95.05, 100, 108.88), (10, 20, 30)]:
        L, a, b = xyz_to_lab(*xyz)
        x2, y2, z2 = lab_to_xyz(L, a, b)
        for u, v in zip(xyz, (x2, y2, z2)):
            assert approx(u, v, 1e-3), (xyz, (x2, y2, z2))
    print("OK: XYZ -> LAB -> XYZ")


def test_hsv_lab_hsv_roundtrip():
    for hsv in [(0, 1, 1), (120, 0.5, 0.8), (300, 0.3, 0.4), (60, 0.1, 0.9)]:
        lab = hsv_to_lab(*hsv)
        h2, s2, v2 = lab_to_hsv(*lab)
        assert approx(h2, hsv[0], 0.5), (hsv, (h2, s2, v2))
        assert approx(s2, hsv[1], 0.01), (hsv, (h2, s2, v2))
        assert approx(v2, hsv[2], 0.01), (hsv, (h2, s2, v2))
    print("OK: HSV -> LAB -> HSV")


def test_hsv_rgb_known():
    r, g, b = hsv_to_rgb(0, 1, 1);   assert (round(r), round(g), round(b)) == (255, 0, 0)
    r, g, b = hsv_to_rgb(120, 1, 1); assert (round(r), round(g), round(b)) == (0, 255, 0)
    r, g, b = hsv_to_rgb(240, 1, 1); assert (round(r), round(g), round(b)) == (0, 0, 255)
    r, g, b = hsv_to_rgb(60, 1, 1);  assert (round(r), round(g), round(b)) == (255, 255, 0)
    print("OK: HSV -> RGB")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"\nВсе {len(tests)} тестов прошли")