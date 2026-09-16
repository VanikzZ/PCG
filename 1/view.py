import tkinter as tk
from tkinter import colorchooser, ttk, messagebox
from controller import ColorController


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HSV ↔ XYZ ↔ LAB")
        self.geometry("700x560")
        self.ctrl = ColorController()
        self._updating = False

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        top = tk.Frame(self); top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="Preview:", font=("Arial", 12, "bold")).pack(side="left")
        self.preview = tk.Canvas(top, width=120, height=60, bg="red",
                                 highlightthickness=1, highlightbackground="black")
        self.preview.pack(side="left", padx=10)
        tk.Button(top, text="Палитра…", command=self.pick_from_palette).pack(side="left")
        tk.Button(top, text="Случайный", command=self.random_color).pack(side="left", padx=5)

        self.hsv_vars = [tk.DoubleVar() for _ in range(3)]
        self.xyz_vars = [tk.DoubleVar() for _ in range(3)]
        self.lab_vars = [tk.DoubleVar() for _ in range(3)]

        self._make_block("HSV", [("H (0..360)", 0, 360), ("S (0..1)", 0, 1), ("V (0..1)", 0, 1)],
                         self.hsv_vars, self.on_hsv_changed, row=1)
        self._make_block("XYZ", [("X (0..100)", 0, 100), ("Y (0..100)", 0, 100), ("Z (0..100)", 0, 100)],
                         self.xyz_vars, self.on_xyz_changed, row=2)
        self._make_block("LAB", [("L (0..100)", 0, 100), ("a (-128..127)", -128, 127), ("b (-128..127)", -128, 127)],
                         self.lab_vars, self.on_lab_changed, row=3)

        self.status = tk.Label(self, text="", fg="#a35", anchor="w", justify="left")
        self.status.pack(fill="x", padx=10, pady=8)

        self.rgb_label = tk.Label(self, text="", font=("Courier", 10))
        self.rgb_label.pack()

    def _make_block(self, title, fields, vars_, callback, row):
        frame = tk.LabelFrame(self, text=title, padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)
        for i, (label, lo, hi) in enumerate(fields):
            tk.Label(frame, text=label, width=14, anchor="w").grid(row=i, column=0, sticky="w")
            e = tk.Entry(frame, textvariable=vars_[i], width=10)
            e.grid(row=i, column=1, padx=4)
            e.bind("<Return>", lambda _e, cb=callback: cb())
            e.bind("<FocusOut>", lambda _e, cb=callback: cb())
            s = ttk.Scale(frame, from_=lo, to=hi, orient="horizontal",
                          variable=vars_[i], command=lambda _v, cb=callback: cb())
            s.grid(row=i, column=2, sticky="ew", padx=4)
            frame.columnconfigure(2, weight=1)

    def on_hsv_changed(self):
        if self._updating: return
        try:
            h, s, v = (var.get() for var in self.hsv_vars)
        except tk.TclError:
            return
        warn = self.ctrl.set_hsv(h, s, v)
        self._refresh_all(skip="hsv", warnings=warn)

    def on_xyz_changed(self):
        if self._updating: return
        try:
            x, y, z = (var.get() for var in self.xyz_vars)
        except tk.TclError:
            return
        warn = self.ctrl.set_xyz(x, y, z)
        self._refresh_all(skip="xyz", warnings=warn)

    def on_lab_changed(self):
        if self._updating: return
        try:
            L, a, b = (var.get() for var in self.lab_vars)
        except tk.TclError:
            return
        warn = self.ctrl.set_lab(L, a, b)
        self._refresh_all(skip="lab", warnings=warn)

    def pick_from_palette(self):
        r, g, b = self.ctrl.get_rgb255()
        rgb, _ = colorchooser.askcolor(color=f"#{r:02x}{g:02x}{b:02x}")
        if rgb is None: return
        r, g, b = rgb
        from model import rgb_to_hsv_public
        h, s, v = rgb_to_hsv_public(r, g, b)
        self.ctrl.set_hsv(h * 360, s, v)
        self._refresh_all()

    def random_color(self):
        import random
        self.ctrl.set_hsv(random.uniform(0, 360), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0))
        self._refresh_all()

    def _refresh_all(self, skip=None, warnings=None):
        self._updating = True
        try:
            if skip != "hsv":
                for var, val in zip(self.hsv_vars, self.ctrl.hsv):
                    var.set(round(val, 3))
            if skip != "xyz":
                for var, val in zip(self.xyz_vars, self.ctrl.xyz):
                    var.set(round(val, 3))
            if skip != "lab":
                for var, val in zip(self.lab_vars, self.ctrl.lab):
                    var.set(round(val, 3))
        finally:
            self._updating = False

        r, g, b = self.ctrl.get_rgb255()
        self.preview.configure(bg=f"#{r:02x}{g:02x}{b:02x}")
        self.rgb_label.config(text=f"RGB (справочно): ({r}, {g}, {b})")

        if warnings:
            self.status.config(text="⚠ " + "; ".join(warnings))
        else:
            self.status.config(text="")