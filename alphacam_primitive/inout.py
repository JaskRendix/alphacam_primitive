from __future__ import annotations

import math
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
    approach_angle: float | None = None,
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

    if offsets.in_dx == offsets.out_dx and offsets.in_dy == offsets.out_dy:
        raise ValueError("in/out offsets are identical — points will coincide")

    if approach_angle is None:
        in_x = path.max_x - offsets.in_dx
        in_y = path.max_y - offsets.in_dy
        out_x = path.max_x - offsets.out_dx
        out_y = path.max_y - offsets.out_dy
        return in_x, in_y, out_x, out_y

    theta = math.radians(approach_angle)
    vx = math.cos(theta)
    vy = math.sin(theta)

    # Pick reference point based on angle quadrant
    if approach_angle % 360 == 0:  # from left → right
        x0 = path.min_x
        y0 = (path.min_y + path.max_y) / 2
    elif approach_angle % 360 == 90:  # from bottom → up
        x0 = (path.min_x + path.max_x) / 2
        y0 = path.min_y
    elif approach_angle % 360 == 180:  # from right → left
        x0 = path.max_x
        y0 = (path.min_y + path.max_y) / 2
    elif approach_angle % 360 == 270:  # from top → down
        x0 = (path.min_x + path.max_x) / 2
        y0 = path.max_y
    else:
        raise ValueError("approach_angle must be one of 0, 90, 180, 270 degrees")

    # Compute points
    in_x = x0 - vx * offsets.in_dx
    in_y = y0 - vy * offsets.in_dy
    out_x = x0 - vx * offsets.out_dx
    out_y = y0 - vy * offsets.out_dy

    return in_x, in_y, out_x, out_y
