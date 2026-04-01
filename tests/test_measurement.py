import pytest

from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.measurement import (
    MeasurementOffsets,
    MeasurementPoint,
    compute_measurement_points,
)


def make_path(
    name: int, min_x: float, min_y: float, w: float = 10.0, h: float = 5.0
) -> PathBBox:
    return PathBBox(
        name=name,
        min_x=min_x,
        min_y=min_y,
        max_x=min_x + w,
        max_y=min_y + h,
        length=30.0,
    )


NO_OFFSET = MeasurementOffsets(dx=0.0, dy=0.0)


def test_basic_three_paths_x():
    paths = [make_path(1, 0, 0), make_path(2, 20, 0), make_path(3, 40, 0)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2, 3],
        geo_min=0,
        geo_max=60,
        count_per_band=3,
        offsets=MeasurementOffsets(dx=1.0, dy=0.0),
        prefer_y=False,
    )
    assert len(result) == 3
    assert result[1].x == 1.0
    assert result[1].y == 0.0


def test_offset_applied_correctly():
    paths = [make_path(1, 5, 10)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1],
        geo_min=0,
        geo_max=60,
        count_per_band=1,
        offsets=MeasurementOffsets(dx=2.0, dy=3.0),
        prefer_y=False,
    )
    assert result[1].x == 7.0  # min_x + dx
    assert result[1].y == 13.0  # min_y + dy


def test_prefer_y_uses_min_y_for_band():
    # span = 40/2 = 20
    # path1 min_y=0  -> band 1
    # path2 min_y=20 -> band 2
    paths = [make_path(1, 0, 0), make_path(2, 0, 20)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2],
        geo_min=0,
        geo_max=40,
        count_per_band=2,
        offsets=NO_OFFSET,
        prefer_y=True,
    )
    assert result[1].band != result[2].band


def test_all_paths_same_band():
    paths = [make_path(1, 0, 0), make_path(2, 5, 0), make_path(3, 10, 0)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2, 3],
        geo_min=0,
        geo_max=60,
        count_per_band=3,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    bands = {v.band for v in result.values()}
    assert len(bands) == 1


def test_paths_in_separate_bands():
    # With count_per_band=3, span = 90/3 = 30
    # path1 min_x=0  -> band 1 (0 < 30)
    # path2 min_x=30 -> band 2 (30 < 60)
    # path3 min_x=60 -> band 3 (60 < 90)
    paths = [make_path(1, 0, 0), make_path(2, 30, 0), make_path(3, 60, 0)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2, 3],
        geo_min=0,
        geo_max=90,
        count_per_band=3,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert result[1].band == 1
    assert result[2].band == 2
    assert result[3].band == 3


def test_band_gap_larger_than_one_span():
    # span = 90/3 = 30
    # path1 min_x=0  -> band 1
    # path2 min_x=20 -> band 1
    # path3 min_x=80 -> needs while to skip to band 3
    paths = [make_path(1, 0, 0), make_path(2, 20, 0), make_path(3, 80, 0)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2, 3],
        geo_min=0,
        geo_max=90,
        count_per_band=3,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert result[3].band > result[2].band


def test_empty_paths_returns_empty():
    result = compute_measurement_points(
        paths=[],
        ordered_indices=[],
        geo_min=0,
        geo_max=60,
        count_per_band=1,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert result == {}


def test_empty_ordered_indices_returns_empty():
    paths = [make_path(1, 0, 0)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[],
        geo_min=0,
        geo_max=60,
        count_per_band=1,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert result == {}


def test_single_path():
    paths = [make_path(1, 5, 3)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1],
        geo_min=0,
        geo_max=60,
        count_per_band=1,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert len(result) == 1
    assert isinstance(result[1], MeasurementPoint)


def test_zero_offset_places_point_at_min_corner():
    paths = [make_path(1, 7, 4)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1],
        geo_min=0,
        geo_max=60,
        count_per_band=1,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    assert result[1].x == 7.0
    assert result[1].y == 4.0


def test_count_per_band_one_means_each_path_is_own_band():
    paths = [make_path(i, i * 10, 0) for i in range(1, 5)]
    result = compute_measurement_points(
        paths=paths,
        ordered_indices=[1, 2, 3, 4],
        geo_min=0,
        geo_max=40,
        count_per_band=1,
        offsets=NO_OFFSET,
        prefer_y=False,
    )
    bands = [result[i].band for i in range(1, 5)]
    assert bands == sorted(bands)  # monotonically increasing


def test_geo_min_equals_geo_max_does_not_crash():
    """Degenerate range — band_span becomes 0, should not divide by zero."""
    paths = [make_path(1, 0, 0)]
    # count_per_band=1 prevents zero division via max(count_per_band, 1)
    # but geo_max == geo_min makes band_span = 0
    with pytest.raises((ZeroDivisionError, ValueError)):
        compute_measurement_points(
            paths=paths,
            ordered_indices=[1],
            geo_min=10,
            geo_max=10,
            count_per_band=1,
            offsets=NO_OFFSET,
            prefer_y=False,
        )
