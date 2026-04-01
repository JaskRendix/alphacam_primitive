from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .geometry import PathBBox, from_paths


@dataclass
class MeasurementPoint:
    x: float
    y: float
    band: int


@dataclass
class MeasurementOffsets:
    dx: float = 0.0
    dy: float = 0.0


def compute_measurement_points(
    paths: Iterable[PathBBox],
    ordered_indices: list[int],
    geo_min: float,
    geo_max: float,
    count_per_band: int,
    offsets: MeasurementOffsets,
    prefer_y: bool,
) -> dict[int, MeasurementPoint]:
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
        dict mapping 1-based path index -> MeasurementPoint
    """
    path_list = from_paths(paths)
    if not path_list or not ordered_indices:
        return {}

    # Map 1-based indices to PathBBox
    index_to_path = {i + 1: p for i, p in enumerate(path_list)}

    measurement: dict[int, MeasurementPoint] = {}

    # Compute band size similar to VB tempGMCount
    band_span = (geo_max - geo_min) / max(count_per_band, 1)
    if band_span <= 0:
        raise ValueError(
            f"Invalid band range: geo_min={geo_min}, geo_max={geo_max}, "
            f"count_per_band={count_per_band} produces band_span={band_span}"
        )
    current_band_max = geo_min + band_span

    current_group_index = 1

    for idx in ordered_indices:
        p = index_to_path[idx]

        coord = p.min_y if prefer_y else p.min_x

        while coord >= current_band_max:
            # Start a new band
            current_band_max += band_span
            current_group_index += 1

        # Place measurement point at a diagonal intersection near min corner
        # VB uses IntersectWithLine with deltaMeasureX/Y; we approximate.
        x = p.min_x + offsets.dx
        y = p.min_y + offsets.dy

        measurement[idx] = MeasurementPoint(x=x, y=y, band=current_group_index)

    return measurement
