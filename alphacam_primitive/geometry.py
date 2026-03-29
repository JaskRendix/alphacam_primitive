from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class PathBBox:
    """
    Minimal abstraction of an Alphacam Path as used in the VB code.

    The VB macro only ever touches:
    - MinXL, MinYL
    - MaxXL, MaxYL
    - Length

    So we model just that.
    """

    name: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    length: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


@dataclass
class GeoRecord:
    """
    Python equivalent of the VB6 GeoClass:

        Ind  -> index in sorted/grouped order
        Name -> original index / identifier
        X,Y  -> representative coordinate (min_x/min_y in VB)
    """

    ind: int
    name: int
    x: float
    y: float


def from_paths(paths: Iterable[PathBBox]) -> list[PathBBox]:
    """
    Convenience helper: normalize an iterable of PathBBox into a list.
    """
    return list(paths)
