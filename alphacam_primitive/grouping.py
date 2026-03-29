from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .geometry import GeoRecord, PathBBox, from_paths


@dataclass
class GroupingResult:
    """
    Result of grouping and ordering geometry.

    - records: GeoRecord entries in processing order
    - path_band_lengths: equivalent of PathXYLen() in VB (length per band)
    """

    records: list[GeoRecord]
    path_band_lengths: tuple[int, int]


def _build_geo_records(paths: list[PathBBox]) -> list[GeoRecord]:
    """
    Equivalent of SetCollectionX/SetCollectionY in VB:
    build a collection of GeoRecord from PathBBox list.
    """
    records: list[GeoRecord] = []
    for i, p in enumerate(paths, start=1):
        # VB: Name = I, Ind = I, X = MinXL, Y = MinYL
        records.append(GeoRecord(ind=i, name=i, x=p.min_x, y=p.min_y))
    return records


def _sort_by_axis(
    records: list[GeoRecord],
    axis: str,
    delta: float,
) -> tuple[list[GeoRecord], tuple[int, int]]:
    """
    Equivalent of SortX / SortY in VB.

    - axis: "x" or "y"
    - delta: band tolerance

    Returns:
        (sorted_records, path_band_lengths)
    """
    remaining = records.copy()
    sorted_records: list[GeoRecord] = []
    s = 0
    path_xy_len = [0, 0]  # VB used PathXYLen(1), PathXYLen(2)

    t = 0  # index into path_xy_len

    while remaining:
        # Find minimal coordinate along chosen axis (integer-rounded)
        if axis == "x":
            temp = min(int(r.x) for r in remaining)
        else:
            temp = min(int(r.y) for r in remaining)

        band: list[GeoRecord] = []
        new_remaining: list[GeoRecord] = []

        for r in remaining:
            coord = int(r.x) if axis == "x" else int(r.y)
            if (temp - delta) < coord < (temp + delta):
                s += 1
                band.append(GeoRecord(ind=s, name=r.name, x=r.x, y=r.y))
            else:
                new_remaining.append(r)

        sorted_records.extend(band)
        remaining = new_remaining

        if t < 2:
            path_xy_len[t] = s
            t = 1  # VB sets T=2 after first assignment; we just keep last

    return sorted_records, (path_xy_len[0], path_xy_len[1])


def build_geo_records(paths: Iterable[PathBBox]) -> list[GeoRecord]:
    """
    Public helper: build GeoRecord list from PathBBox iterable.
    """
    return _build_geo_records(from_paths(paths))


def order_geo(
    paths: Iterable[PathBBox],
    prefer_y: bool,
) -> tuple[list[int], tuple[int, int]]:
    """
    High-level equivalent of OrderGeo in VB.

    - prefer_y: if True, group primarily along Y (then sort by X),
                otherwise group along X (then sort by Y).

    Returns:
        (ordered_indices, path_band_lengths)

    ordered_indices are 1-based indices into the original paths list,
    matching the VB behavior where Name = original index.
    """
    path_list = from_paths(paths)
    if not path_list:
        return [], (0, 0)

    # VB uses deltaX/deltaY as (Max - Min - 2) of first geometry
    delta_y = round(path_list[0].height - 2)
    delta_x = round(path_list[0].width - 2)

    records = _build_geo_records(path_list)

    if prefer_y:
        # SetCollectionY + SortX
        grouped, path_xy_len = _sort_by_axis(records, axis="y", delta=delta_y)
        grouped, path_xy_len = _sort_by_axis(grouped, axis="x", delta=delta_x)
    else:
        # SetCollectionX + SortY
        grouped, path_xy_len = _sort_by_axis(records, axis="x", delta=delta_x)
        grouped, path_xy_len = _sort_by_axis(grouped, axis="y", delta=delta_y)

    ordered_indices = [r.name for r in grouped]
    return ordered_indices, path_xy_len
