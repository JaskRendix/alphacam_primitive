from __future__ import annotations

from dataclasses import dataclass

from .geometry import PathBBox


@dataclass
class InOutOffsets:
    """
    Offsets used in the VB inOut() function:

    - DIx, DIy: inside offset
    - DOx, DOy: outside offset
    """

    in_dx: float
    in_dy: float
    out_dx: float
    out_dy: float


def compute_inout_points(
    path: PathBBox,
    offsets: InOutOffsets,
) -> tuple[float, float, float, float]:
    """
    Modern equivalent of VB inOut(Geo, DIx, DIy, DOx, DOy).

    The original code calls Geo.IntersectWithLine from:
        (MinXL, MinYL) to (MaxXL - DIx, MaxYL - DIy)
    and similarly for DOx/DOy, then picks the "furthest" intersection.

    Here we assume the geometry is approximated by its bounding box and
    compute the in/out points along the diagonal directions.

    Returns:
        (in_x, in_y, out_x, out_y)
    """
    # Inside point: along diagonal from min to max with inside offsets
    in_x = path.max_x - offsets.in_dx
    in_y = path.max_y - offsets.in_dy

    # Outside point: along diagonal from min to max with outside offsets
    out_x = path.max_x - offsets.out_dx
    out_y = path.max_y - offsets.out_dy

    return in_x, in_y, out_x, out_y
