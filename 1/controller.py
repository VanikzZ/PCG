from model import (
    hsv_to_xyz, xyz_to_lab,
    xyz_to_hsv, lab_to_xyz,
    hsv_to_rgb255,
)


class ColorController:
    def __init__(self):
        self.hsv = (0.0, 1.0, 1.0)
        self.xyz = (0.0, 0.0, 0.0)
        self.lab = (0.0, 0.0, 0.0)
        self._recalc_from_hsv()

    def _recalc_from_hsv(self):
        self.xyz = hsv_to_xyz(*self.hsv)
        self.lab = xyz_to_lab(*self.xyz)

    def _recalc_from_xyz(self):
        self.hsv = xyz_to_hsv(*self.xyz)
        self.lab = xyz_to_lab(*self.xyz)

    def _recalc_from_lab(self):
        self.xyz = lab_to_xyz(*self.lab)
        self.hsv = xyz_to_hsv(*self.xyz)

    def set_hsv(self, h, s, v):
        warnings = []
        if not (0 <= h <= 360):
            warnings.append(f"H обрезан: {h:.2f} -> {h % 360:.2f}")
        if not (0 <= s <= 1):
            warnings.append(f"S обрезан: {s:.4f}")
        if not (0 <= v <= 1):
            warnings.append(f"V обрезан: {v:.4f}")
        self.hsv = (h % 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
        self._recalc_from_hsv()
        return warnings

    def set_xyz(self, x, y, z):
        warnings = []
        if any(not (0 <= c <= 100) for c in (x, y, z)):
            warnings.append("XYZ вне 0..100 — цвет вне гаммы sRGB, RGB будет обрезан")
        self.xyz = (x, y, z)
        self._recalc_from_xyz()
        return warnings

    def set_lab(self, L, a, b):
        warnings = []
        if not (0 <= L <= 100):
            warnings.append(f"L обрезан: {L:.2f}")
        self.lab = (max(0.0, min(100.0, L)), a, b)
        self._recalc_from_lab()
        return warnings

    def get_rgb255(self):
        return hsv_to_rgb255(*self.hsv)