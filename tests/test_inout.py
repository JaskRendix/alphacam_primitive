import pytest

from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.inout import InOutOffsets, compute_inout_points


def test_compute_inout_points_basic():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(in_dx=1, in_dy=2, out_dx=3, out_dy=4)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert (in_x, in_y) == (9, 3)
    assert (out_x, out_y) == (7, 1)


def test_compute_inout_points_negative_offsets():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(in_dx=-2, in_dy=-3, out_dx=-4, out_dy=-5)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    # max_x - (-2) = 12, max_y - (-3) = 8
    assert (in_x, in_y) == (12, 8)
    assert (out_x, out_y) == (14, 10)


def test_compute_inout_points_zero_offsets():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(in_dx=0, in_dy=0, out_dx=5, out_dy=5)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert (in_x, in_y) == (10, 5)
    assert (out_x, out_y) == (5, 0)


def test_compute_inout_points_rectangular_bbox():
    p = PathBBox(1, 0, 0, 100, 10, 30)
    offsets = InOutOffsets(in_dx=10, in_dy=1, out_dx=20, out_dy=2)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert (in_x, in_y) == (90, 9)
    assert (out_x, out_y) == (80, 8)


def test_compute_inout_points_large_coordinates():
    p = PathBBox(1, 1000, 2000, 3000, 4000, 0)
    offsets = InOutOffsets(in_dx=10, in_dy=20, out_dx=30, out_dy=40)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert (in_x, in_y) == (2990, 3980)
    assert (out_x, out_y) == (2970, 3960)


def test_compute_inout_points_degenerate_bbox():
    # zero‑size rectangle
    p = PathBBox(1, 5, 5, 5, 5, 0)
    offsets = InOutOffsets(in_dx=1, in_dy=1, out_dx=2, out_dy=2)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert (in_x, in_y) == (4, 4)
    assert (out_x, out_y) == (3, 3)


def test_compute_inout_points_identical_offsets_raises():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(in_dx=2, in_dy=2, out_dx=2, out_dy=2)

    with pytest.raises(ValueError):
        compute_inout_points(p, offsets)


def test_compute_inout_points_float_precision():
    p = PathBBox(1, 0, 0, 10.5, 5.25, 30)
    offsets = InOutOffsets(in_dx=0.5, in_dy=0.25, out_dx=1.5, out_dy=1.25)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert in_x == pytest.approx(10.0)
    assert in_y == pytest.approx(5.0)
    assert out_x == pytest.approx(9.0)
    assert out_y == pytest.approx(4.0)
