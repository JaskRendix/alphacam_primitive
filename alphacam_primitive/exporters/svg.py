from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ..geometry import PathBBox
from ..measurement import MeasurementPoint


def _rect(
    p: PathBBox,
    stroke: str = "black",
    stroke_width: float = 1.0,
    fill: str = "none",
) -> str:
    return (
        f'<rect x="{p.min_x}" y="{-p.max_y}" '
        f'width="{p.width}" height="{p.height}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'
    )


def _inout_circle(
    x: float,
    y: float,
    kind: str,
    radius: float = 2.0,
) -> str:
    """
    kind: "in" or "out"
    """
    return (
        f'<circle cx="{x}" cy="{-y}" r="{radius}" '
        f'class="inout-point {kind}-point" data-type="{kind}" />'
    )


def _measure_point(
    pt: MeasurementPoint,
    radius: float = 1.5,
) -> str:
    return (
        f'<circle cx="{pt.x}" cy="{-pt.y}" r="{radius}" '
        f'class="measure-point" data-measure="1" />'
    )


def _measure_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> str:
    return (
        f'<line x1="{x1}" y1="{-y1}" x2="{x2}" y2="{-y2}" '
        f'class="measure-line" data-measure="1" />'
    )


def _band_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    index: int,
) -> str:
    return (
        f'<rect x="{x}" y="{-y - height}" width="{width}" height="{height}" '
        f'class="band-rect" data-band="{index}" />'
    )


def export_svg_unified(
    paths: Iterable[PathBBox],
    out_path: Path,
    *,
    measurement_points: dict[int, MeasurementPoint] | None = None,
    measurement_lines: list[tuple[float, float, float, float]] | None = None,
    include_bands: bool = False,
    band_count: int = 5,
) -> None:
    """
    Export a unified SVG containing:
      - rectangles
      - in/out points
      - measurement points
      - measurement diagonals
      - optional grouping bands

    This is intended for debugging and visualization.
    """

    paths_list: list[PathBBox] = list(paths)
    if not paths_list:
        out_path.write_text("<svg></svg>")
        return

    min_x: float = min(p.min_x for p in paths_list)
    min_y: float = min(p.min_y for p in paths_list)
    max_x: float = max(p.max_x for p in paths_list)
    max_y: float = max(p.max_y for p in paths_list)

    width: float = max_x - min_x
    height: float = max_y - min_y

    rect_layer: list[str] = []
    inout_layer: list[str] = []
    measure_point_layer: list[str] = []
    measure_line_layer: list[str] = []
    band_layer: list[str] = []

    for p in paths_list:
        rect_layer.append(_rect(p))

        if getattr(p, "in_point", None) is not None:
            ip = p.in_point
            inout_layer.append(_inout_circle(ip.x, ip.y, "in"))

        if getattr(p, "out_point", None) is not None:
            op = p.out_point
            inout_layer.append(_inout_circle(op.x, op.y, "out"))

    if measurement_points:
        for pt in measurement_points.values():
            measure_point_layer.append(_measure_point(pt))

    if measurement_lines:
        for x1, y1, x2, y2 in measurement_lines:
            measure_line_layer.append(_measure_line(x1, y1, x2, y2))

    if include_bands and band_count > 0:
        band_height: float = height / band_count
        for i in range(band_count):
            y0: float = min_y + i * band_height
            band_layer.append(_band_rect(min_x, y0, width, band_height, i))

    svg_parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x} {-max_y} {width} {height}">',
        '<g id="bands">',
        *band_layer,
        "</g>",
        '<g id="rectangles">',
        *rect_layer,
        "</g>",
        '<g id="inout">',
        *inout_layer,
        "</g>",
        '<g id="measure-points">',
        *measure_point_layer,
        "</g>",
        '<g id="measure-lines">',
        *measure_line_layer,
        "</g>",
        "</svg>",
    ]

    out_path.write_text("\n".join(svg_parts))
