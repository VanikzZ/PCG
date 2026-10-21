import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog

from core.engine import ScanEngine
from core.models import ImageInfo

COLUMNS = [
    ("filename", "Файл", 200),
    ("fmt", "Формат", 70),
    ("width", "Ширина", 70),
    ("height", "Высота", 70),
    ("dpi_x", "DPI X", 70),
    ("dpi_y", "DPI Y", 70),
    ("bit_depth", "Глубина", 70),
    ("color_type", "Тип цвета", 130),
    ("compression", "Сжатие", 160),
    ("status", "Статус", 110),
    ("error", "Ошибка", 250),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №2 — Метаданные изображений")
        self.geometry("1400x750")

        self.engine = None
        self.scan_thread = None

        self._build_ui()

    def _build_ui(self):
        top_frame = tk.Frame(self, pady=5, padx=10)
        top_frame.pack(fill=tk.X)

        self.btn_select = tk.Button(top_frame, text="Выбрать папку", command=self.select_folder)
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_scan = tk.Button(top_frame, text="Сканировать", command=self.start_scan, state=tk.DISABLED)
        self.btn_scan.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(top_frame, text="Стоп", command=self.stop_scan, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.folder_var = tk.StringVar(value="Папка не выбрана")
        tk.Label(top_frame, textvariable=self.folder_var, fg="gray").pack(side=tk.LEFT, padx=15)


        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=[c[0] for c in COLUMNS], show="headings")
        for col_id, col_name, col_width in COLUMNS:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=col_width, anchor=tk.W, stretch=False)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.tag_configure("corrupted", background="#ffcccc")
        self.tree.tag_configure("mismatch", background="#fff3cd")

        bottom_frame = tk.Frame(self, pady=5, padx=10)
        bottom_frame.pack(fill=tk.X)

        self.progress = ttk.Progressbar(bottom_frame, orient="horizontal", mode="determinate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.status_var = tk.StringVar(value="0 / 0")
        tk.Label(bottom_frame, textvariable=self.status_var, width=15).pack(side=tk.RIGHT)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.btn_scan.config(state=tk.NORMAL)

    def start_scan(self):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.btn_select.config(state=tk.DISABLED)
        self.btn_scan.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self.status_var.set("0 / 0")

        self.engine = ScanEngine()

        self.scan_thread = threading.Thread(
            target=self.engine.scan,
            args=(folder, self.on_result, self.on_progress),
            daemon=True,
        )
        self.scan_thread.start()

    def stop_scan(self):
        if self.engine:
            self.engine.stop()
        self.btn_stop.config(state=tk.DISABLED)

    def on_result(self, info: ImageInfo):
        self.after(0, self._insert_row, info)

    def on_progress(self, done: int, total: int):
        self.after(0, self._update_progress, done, total)

    def _insert_row(self, info: ImageInfo):
        values = (
            info.filename,
            info.fmt,
            info.width if info.width is not None else "-",
            info.height if info.height is not None else "-",
            info.dpi_x if info.dpi_x is not None else "-",
            info.dpi_y if info.dpi_y is not None else "-",
            info.bit_depth if info.bit_depth is not None else "-",
            info.color_type,
            info.compression,
            info.status,
            info.error,
        )
        tags = ()
        if info.status == "CORRUPTED":
            tags = ("corrupted",)
        elif info.status == "EXT_MISMATCH":
            tags = ("mismatch",)

        self.tree.insert("", tk.END, values=values, tags=tags)

    def _update_progress(self, done: int, total: int):
        self.progress["maximum"] = total if total > 0 else 1
        self.progress["value"] = done
        self.status_var.set(f"{done} / {total}")

        if done >= total:
            self.btn_select.config(state=tk.NORMAL)
            self.btn_scan.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)