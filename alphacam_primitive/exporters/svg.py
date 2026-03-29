from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

from ..geometry import PathBBox
from ..measurement import MeasurementPoint


def export_rectangles_svg(
    paths: Iterable[PathBBox],
    out_path: Path,
    stroke="black",
    stroke_width=1,
    fill="none",
) -> None:
    """
    Export PathBBox rectangles as SVG <rect> elements.
    """
    rects = []
    min_x = min(p.min_x for p in paths)
    min_y = min(p.min_y for p in paths)
    max_x = max(p.max_x for p in paths)
    max_y = max(p.max_y for p in paths)

    width = max_x - min_x
    height = max_y - min_y

    for p in paths:
        rects.append(
            f'<rect x="{p.min_x}" y="{-p.max_y}" '
            f'width="{p.width}" height="{p.height}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x} {-max_y} {width} {height}">\n'
        + "\n".join(rects)
        + "\n</svg>"
    )

    out_path.write_text(svg)


def export_measurement_points_svg(
    points: Dict[int, MeasurementPoint],
    out_path: Path,
    radius=1.5,
    stroke="red",
    fill="red",
) -> None:
    """
    Export measurement points as SVG <circle> elements.
    """
    if not points:
        out_path.write_text("<svg></svg>")
        return

    xs = [pt.x for pt in points.values()]
    ys = [pt.y for pt in points.values()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x or 10
    height = max_y - min_y or 10

    circles = [
        f'<circle cx="{pt.x}" cy="{-pt.y}" r="{radius}" stroke="{stroke}" fill="{fill}" />'
        for pt in points.values()
    ]

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x} {-max_y} {width} {height}">\n'
        + "\n".join(circles)
        + "\n</svg>"
    )

    out_path.write_text(svg)
