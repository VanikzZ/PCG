import tkinter as tk
from tkinter import colorchooser, ttk

from controller import ColorController


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лаба: HSV ↔ XYZ ↔ LAB")
        self.geometry("780x640")
        self.ctrl = ColorController()
        self._updating = False

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        top = tk.Frame(self); top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="Превью:", font=("Arial", 12, "bold")).pack(side="left")
        self.preview = tk.Canvas(top, width=140, height=70, bg="#ff0000",
                                 highlightthickness=1, highlightbackground="black")
        self.preview.pack(side="left", padx=10)
        tk.Button(top, text="Палитра…", command=self.pick_from_palette).pack(side="left")
        tk.Button(top, text="Случайный", command=self.random_color).pack(side="left", padx=5)

        self.hsv_scale_vars = [tk.DoubleVar() for _ in range(3)]
        self.xyz_scale_vars = [tk.DoubleVar() for _ in range(3)]
        self.lab_scale_vars = [tk.DoubleVar() for _ in range(3)]
        self.hsv_entry_vars = [tk.StringVar() for _ in range(3)]
        self.xyz_entry_vars = [tk.StringVar() for _ in range(3)]
        self.lab_entry_vars = [tk.StringVar() for _ in range(3)]

        self._make_block("HSV",
                         [("H (0..360)", 0, 360), ("S (0..1)", 0, 1), ("V (0..1)", 0, 1)],
                         self.hsv_scale_vars, self.hsv_entry_vars,
                         self.on_hsv_scale, self.on_hsv_entry)
        self._make_block("XYZ",
                         [("X (0..100)", 0, 100), ("Y (0..100)", 0, 100), ("Z (0..100)", 0, 100)],
                         self.xyz_scale_vars, self.xyz_entry_vars,
                         self.on_xyz_scale, self.on_xyz_entry)
        self._make_block("LAB",
                         [("L (0..100)", 0, 100), ("a (-128..127)", -128, 127), ("b (-128..127)", -128, 127)],
                         self.lab_scale_vars, self.lab_entry_vars,
                         self.on_lab_scale, self.on_lab_entry)

        self.status = tk.Label(self, text="", fg="#a35", anchor="w", justify="left")
        self.status.pack(fill="x", padx=10, pady=8)
        self.rgb_label = tk.Label(self, text="", font=("Courier", 10))
        self.rgb_label.pack()

    def _make_block(self, title, fields, scale_vars, entry_vars, on_scale, on_entry):
        frame = tk.LabelFrame(self, text=title, padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)
        for i, (label, lo, hi) in enumerate(fields):
            tk.Label(frame, text=label, width=14, anchor="w")\
                .grid(row=i, column=0, sticky="w")

            e = tk.Entry(frame, textvariable=entry_vars[i], width=10)
            e.grid(row=i, column=1, padx=4)
            e.bind("<Return>",   lambda _e, cb=on_entry: cb())
            e.bind("<FocusOut>", lambda _e, cb=on_entry: cb())

            s = ttk.Scale(frame, from_=lo, to=hi, orient="horizontal",
                          variable=scale_vars[i],
                          command=lambda v, cb=on_scale, idx=i: cb(idx, v))
            s.grid(row=i, column=2, sticky="ew", padx=4)
            frame.columnconfigure(2, weight=1)

    def on_hsv_scale(self, idx, val):
        if self._updating: return
        vals = list(self.ctrl.hsv)
        vals[idx] = float(val)
        warn = self.ctrl.set_hsv(*vals)
        self._refresh_all(skip_scale="hsv", warnings=warn)

    def on_xyz_scale(self, idx, val):
        if self._updating: return
        vals = list(self.ctrl.xyz)
        vals[idx] = float(val)
        warn = self.ctrl.set_xyz(*vals)
        self._refresh_all(skip_scale="xyz", warnings=warn)

    def on_lab_scale(self, idx, val):
        if self._updating: return
        vals = list(self.ctrl.lab)
        vals[idx] = float(val)
        warn = self.ctrl.set_lab(*vals)
        self._refresh_all(skip_scale="lab", warnings=warn)

    def _read_entries(self, scale_vars, entry_vars):
        result = []
        for sv, ev in zip(scale_vars, entry_vars):
            text = ev.get().strip().replace(",", ".")
            if not text:
                result.append(float(sv.get()))
                continue
            try:
                result.append(float(text))
            except ValueError:
                result.append(float(sv.get()))
        return result

    def on_hsv_entry(self):
        if self._updating: return
        vals = self._read_entries(self.hsv_scale_vars, self.hsv_entry_vars)
        warn = self.ctrl.set_hsv(*vals)
        self._refresh_all(warnings=warn)

    def on_xyz_entry(self):
        if self._updating: return
        vals = self._read_entries(self.xyz_scale_vars, self.xyz_entry_vars)
        warn = self.ctrl.set_xyz(*vals)
        self._refresh_all(warnings=warn)

    def on_lab_entry(self):
        if self._updating: return
        vals = self._read_entries(self.lab_scale_vars, self.lab_entry_vars)
        warn = self.ctrl.set_lab(*vals)
        self._refresh_all(warnings=warn)

    def pick_from_palette(self):
        r, g, b = self.ctrl.get_rgb255()
        rgb, _ = colorchooser.askcolor(color=f"#{r:02x}{g:02x}{b:02x}")
        if rgb is None:
            return
        r, g, b = rgb
        R, G, B = r / 255.0, g / 255.0, b / 255.0
        mx, mn = max(R, G, B), min(R, G, B)
        d = mx - mn
        if d == 0:    h = 0.0
        elif mx == R: h = 60.0 * (((G - B) / d) % 6)
        elif mx == G: h = 60.0 * ((B - R) / d + 2)
        else:         h = 60.0 * ((R - G) / d + 4)
        s = 0.0 if mx == 0 else d / mx
        v = mx
        self.ctrl.set_hsv(h, s, v)
        self._refresh_all()

    def random_color(self):
        import random
        self.ctrl.set_hsv(random.uniform(0, 360),
                          random.uniform(0.5, 1.0),
                          random.uniform(0.5, 1.0))
        self._refresh_all()

    def _refresh_all(self, skip_scale=None, warnings=None):
        self._updating = True
        try:
            self._fill(self.hsv_scale_vars, self.hsv_entry_vars, self.ctrl.hsv,
                       skip_scale=(skip_scale == "hsv"))
            self._fill(self.xyz_scale_vars, self.xyz_entry_vars, self.ctrl.xyz,
                       skip_scale=(skip_scale == "xyz"))
            self._fill(self.lab_scale_vars, self.lab_entry_vars, self.ctrl.lab,
                       skip_scale=(skip_scale == "lab"))
        finally:
            self._updating = False

        r, g, b = self.ctrl.get_rgb255()
        self.preview.configure(bg=f"#{r:02x}{g:02x}{b:02x}")
        self.rgb_label.config(text=f"RGB (справочно): ({r}, {g}, {b})")
        self.status.config(text=("⚠ " + "; ".join(warnings)) if warnings else "")

    def _fill(self, scale_vars, entry_vars, values, skip_scale=False):
        if scale_vars is self.hsv_scale_vars:
            formats = [lambda v: str(int(round(v))),
                       lambda v: f"{v:.2f}",
                       lambda v: f"{v:.2f}"]
        elif scale_vars is self.xyz_scale_vars:
            formats = [lambda v: str(int(round(v))),
                       lambda v: str(int(round(v))),
                       lambda v: str(int(round(v)))]
        else:
            formats = [lambda v: str(int(round(v))),
                       lambda v: str(int(round(v))),
                       lambda v: str(int(round(v)))]

        for i, (sv, ev, val) in enumerate(zip(scale_vars, entry_vars, values)):
            if not skip_scale:
                sv.set(val)
            ev.set(formats[i](val))