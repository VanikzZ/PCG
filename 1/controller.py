from model import (
    hsv_to_xyz, xyz_to_lab_public, lab_to_xyz_public,
    xyz_to_hsv, hsv_to_rgb_public, rgb_to_hsv_public,
)


class ColorController:
    def __init__(self):
        self.hsv = (0.0, 1.0, 1.0)
        self.xyz = (0.0, 0.0, 0.0)
        self.lab = (0.0, 0.0, 0.0)
        self._recalc_from_hsv()

    def _recalc_from_hsv(self):
        self.xyz = hsv_to_xyz(*self.hsv)
        self.lab = xyz_to_lab_public(*self.xyz)

    def _recalc_from_xyz(self):
        self.hsv = xyz_to_hsv(*self.xyz)
        self.lab = xyz_to_lab_public(*self.xyz)

    def _recalc_from_lab(self):
        self.xyz = lab_to_xyz_public(*self.lab)
        self.hsv = xyz_to_hsv(*self.xyz)

    def set_hsv(self, h, s, v):
        warnings = []
        if not (0 <= h <= 360):
            warnings.append(f"H обрезан: {h:.1f} -> {h % 360:.1f}")
        if not (0 <= s <= 1):
            warnings.append(f"S обрезан: {s:.3f}")
        if not (0 <= v <= 1):
            warnings.append(f"V обрезан: {v:.3f}")
        self.hsv = (h % 360, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
        self._recalc_from_hsv()
        return warnings

    def set_xyz(self, x, y, z):
        warnings = []
        if x < 0 or y < 0 or z < 0 or x > 100 or y > 100 or z > 100:
            warnings.append("XYZ вне диапазона 0..100 — возможна обрезка при переводе в RGB")
        self.xyz = (x, y, z)
        self._recalc_from_xyz()
        r, g, b = hsv_to_rgb_public(*self.hsv)
        if any(c < -0.5 or c > 255.5 for c in (r, g, b)):
            warnings.append("RGB вышел за [0,255] — цвет обрезан (вне гаммы sRGB)")
        return warnings

    def set_lab(self, L, a, b):
        warnings = []
        if not (0 <= L <= 100):
            warnings.append(f"L обрезан: {L:.2f}")
        self.lab = (max(0.0, min(100.0, L)), a, b)
        self._recalc_from_lab()
        r, g, bb = hsv_to_rgb_public(*self.hsv)
        if any(c < -0.5 or c > 255.5 for c in (r, g, bb)):
            warnings.append("Цвет вне гаммы sRGB — значения RGB обрезаны")
        return warnings

    def get_rgb(self):
        return hsv_to_rgb_public(*self.hsv)

    def get_rgb255(self):
        r, g, b = self.get_rgb()
        return (int(round(max(0, min(255, r)))),
                int(round(max(0, min(255, g)))),
                int(round(max(0, min(255, b)))))