from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ImageInfo:
    filename: str = ""
    fmt: str = "?"
    width: Optional[int] = None
    height: Optional[int] = None
    dpi_x: Optional[float] = None
    dpi_y: Optional[float] = None
    bit_depth: Optional[int] = None
    color_type: str = ""
    compression: str = ""
    extra: dict = field(default_factory=dict)
    status: str = "OK"
    error: str = ""