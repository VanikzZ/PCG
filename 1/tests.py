from model import (
    hsv_to_xyz, xyz_to_hsv,
    xyz_to_lab, lab_to_xyz,
    hsv_to_lab, lab_to_hsv,
)


def approx(a, b, eps=1e-2):
    return abs(a - b) <= eps


def test_red_lab():
    L, a, b = hsv_to_lab(0, 1, 1)
    assert approx(L, 53.24, 0.5), L
    assert approx(a, 80.09, 0.5), a
    assert approx(b, 67.20, 0.5), b
    print("OK: HSV(0,1,1) -> LAB ≈ (53.24, 80.09, 67.20)")


def test_white_lab():
    L, a, b = hsv_to_lab(0, 0, 1)
    assert approx(L, 100, 0.1) and approx(a, 0, 0.1) and approx(b, 0, 0.1)
    print("OK: белый -> LAB ≈ (100, 0, 0)")


def test_black_lab():
    L, a, b = hsv_to_lab(0, 0, 0)
    assert approx(L, 0, 0.1) and approx(a, 0, 0.1) and approx(b, 0, 0.1)
    print("OK: чёрный -> LAB ≈ (0, 0, 0)")


def test_xyz_lab_roundtrip():
    for xyz in [(41.24, 21.26, 1.93), (95.05, 100, 108.88), (10, 20, 30)]:
        lab = xyz_to_lab(*xyz)
        x2, y2, z2 = lab_to_xyz(*lab)
        for u, v in zip(xyz, (x2, y2, z2)):
            assert approx(u, v, 1e-3), (xyz, (x2, y2, z2))
    print("OK: XYZ -> LAB -> XYZ")


def test_hsv_xyz_roundtrip():
    for hsv in [(0, 1, 1), (120, 0.5, 0.8), (300, 0.3, 0.4), (60, 0.1, 0.9)]:
        xyz = hsv_to_xyz(*hsv)
        h2, s2, v2 = xyz_to_hsv(*xyz)
        assert approx(h2, hsv[0], 0.5), (hsv, (h2, s2, v2))
        assert approx(s2, hsv[1], 0.01), (hsv, (h2, s2, v2))
        assert approx(v2, hsv[2], 0.01), (hsv, (h2, s2, v2))
    print("OK: HSV -> XYZ -> HSV")


def test_hsv_lab_roundtrip():
    for hsv in [(0, 1, 1), (120, 0.5, 0.8), (300, 0.3, 0.4)]:
        lab = hsv_to_lab(*hsv)
        h2, s2, v2 = lab_to_hsv(*lab)
        assert approx(h2, hsv[0], 0.5), (hsv, (h2, s2, v2))
        assert approx(s2, hsv[1], 0.01), (hsv, (h2, s2, v2))
        assert approx(v2, hsv[2], 0.01), (hsv, (h2, s2, v2))
    print("OK: HSV -> LAB -> HSV")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"\nВсе {len(tests)} тестов прошли ✔")