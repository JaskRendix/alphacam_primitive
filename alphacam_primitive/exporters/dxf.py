from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

from ..geometry import PathBBox
from ..measurement import MeasurementPoint


def _dxf_header() -> str:
    return "0\nSECTION\n2\nHEADER\n0\nENDSEC\n" "0\nSECTION\n2\nENTITIES\n"


def _dxf_footer() -> str:
    return "0\nENDSEC\n0\nEOF\n"


def _dxf_line(x1, y1, x2, y2) -> str:
    return "0\nLINE\n" "8\n0\n" f"10\n{x1}\n20\n{y1}\n" f"11\n{x2}\n21\n{y2}\n"


def _dxf_point(x, y) -> str:
    return "0\nPOINT\n" "8\n0\n" f"10\n{x}\n20\n{y}\n"


def export_rectangles(
    paths: Iterable[PathBBox],
    out_path: Path,
) -> None:
    """
    Export PathBBox rectangles as DXF LINE entities.
    """
    parts = [_dxf_header()]

    for p in paths:
        x1, y1 = p.min_x, p.min_y
        x2, y2 = p.max_x, p.min_y
        x3, y3 = p.max_x, p.max_y
        x4, y4 = p.min_x, p.max_y

        parts.append(_dxf_line(x1, y1, x2, y2))
        parts.append(_dxf_line(x2, y2, x3, y3))
        parts.append(_dxf_line(x3, y3, x4, y4))
        parts.append(_dxf_line(x4, y4, x1, y1))

    parts.append(_dxf_footer())
    out_path.write_text("".join(parts))


def export_measurement_points(
    points: Dict[int, MeasurementPoint],
    out_path: Path,
) -> None:
    """
    Export measurement points as DXF POINT entities.
    """
    parts = [_dxf_header()]

    for idx, pt in points.items():
        parts.append(_dxf_point(pt.x, pt.y))

    parts.append(_dxf_footer())
    out_path.write_text("".join(parts))
