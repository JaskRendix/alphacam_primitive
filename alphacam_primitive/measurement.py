from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .geometry import PathBBox, from_paths


@dataclass
class MeasurementPoint:
    """
    Equivalent of the measurement points stored in the VB Dictionary:

        key -> (x, y)
    """

    x: float
    y: float


def compute_measurement_points(
    paths: Iterable[PathBBox],
    ordered_indices: list[int],
    geo_min: float,
    geo_max: float,
    count_per_band: int,
    delta_measure: float,
    prefer_y: bool,
) -> tuple[dict[int, MeasurementPoint], list[int]]:
    """
    Modern, simplified equivalent of CountGeo().

    The VB code:
    - walks geometries in a specific order (NG / ArrGeo)
    - accumulates length until a threshold or band limit is reached
    - computes an intersection point along a diagonal
    - stores it in a Dictionary keyed by CountG(NamberGeo)

    Here we:
    - walk paths in ordered_indices order
    - group them into bands based on geo_min/geo_max and count_per_band
    - place a measurement point near the "entry" corner of each band

    Returns:
        (measurement_points, count_g)

        measurement_points: dict[index] -> MeasurementPoint
        count_g: list of indices where measurement points are placed
    """
    path_list = from_paths(paths)
    if not path_list or not ordered_indices:
        return {}, []

    # Map 1-based indices to PathBBox
    index_to_path = {i + 1: p for i, p in enumerate(path_list)}

    measurement: dict[int, MeasurementPoint] = {}
    count_g: list[int] = []

    # Compute band size similar to VB tempGMCount
    band_span = (geo_max - geo_min) / max(count_per_band, 1)
    current_band_max = geo_min + band_span

    current_group_index = 1

    for idx in ordered_indices:
        p = index_to_path[idx]

        coord = p.min_y if prefer_y else p.min_x

        if coord > current_band_max:
            # Start a new band
            current_band_max += band_span
            current_group_index += 1

        # Place measurement point at a diagonal intersection near min corner
        # VB uses IntersectWithLine with deltaMeasureX/Y; we approximate.
        if delta_measure >= 0:
            dx = delta_measure
            dy = 0.0
        else:
            dx = 0.0
            dy = abs(delta_measure)

        x = p.min_x + dx
        y = p.min_y + dy

        measurement[idx] = MeasurementPoint(x=x, y=y)
        count_g.append(idx)

    return measurement, count_g
