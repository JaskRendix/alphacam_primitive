"""
alphacam_primitive

Modern Python rewrite of the core geometry/grouping/ordering logic
from the legacy Alphacam "Primitive" macro.

This package is intentionally independent of Alphacam and operates
on simple geometric abstractions (bounding boxes, lengths).
"""

from .geometry import GeoRecord, PathBBox
from .grouping import build_geo_records, order_geo
from .inout import compute_inout_points
from .measurement import compute_measurement_points

__all__ = [
    "GeoRecord",
    "PathBBox",
    "order_geo",
    "build_geo_records",
    "compute_inout_points",
    "compute_measurement_points",
]
