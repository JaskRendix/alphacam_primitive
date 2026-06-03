import pytest

from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.inout import InOutOffsets, compute_inout_points


@pytest.mark.parametrize(
    "path, offsets, expected",
    [
        # Basic diagonal case
        (
            PathBBox(1, 0, 0, 10, 5, 30),
            InOutOffsets(1, 2, 3, 4),
            (9, 3, 7, 1),
        ),
        # Negative offsets
        (
            PathBBox(1, 0, 0, 10, 5, 30),
            InOutOffsets(-2, -3, -4, -5),
            (12, 8, 14, 10),
        ),
        # Zero inside offset
        (
            PathBBox(1, 0, 0, 10, 5, 30),
            InOutOffsets(0, 0, 5, 5),
            (10, 5, 5, 0),
        ),
        # Rectangular bbox
        (
            PathBBox(1, 0, 0, 100, 10, 30),
            InOutOffsets(10, 1, 20, 2),
            (90, 9, 80, 8),
        ),
        # Large coordinates
        (
            PathBBox(1, 1000, 2000, 3000, 4000, 0),
            InOutOffsets(10, 20, 30, 40),
            (2990, 3980, 2970, 3960),
        ),
        # Degenerate bbox (point)
        (
            PathBBox(1, 5, 5, 5, 5, 0),
            InOutOffsets(1, 1, 2, 2),
            (4, 4, 3, 3),
        ),
    ],
)
def test_compute_inout_points_parametrized(path, offsets, expected):
    assert compute_inout_points(path, offsets) == expected


def test_compute_inout_points_identical_offsets_raises():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(2, 2, 2, 2)

    with pytest.raises(ValueError):
        compute_inout_points(p, offsets)


@pytest.mark.parametrize(
    "path, offsets, expected",
    [
        (
            PathBBox(1, 0, 0, 10.5, 5.25, 30),
            InOutOffsets(0.5, 0.25, 1.5, 1.25),
            (10.0, 5.0, 9.0, 4.0),
        ),
    ],
)
def test_compute_inout_points_float_precision(path, offsets, expected):
    in_x, in_y, out_x, out_y = compute_inout_points(path, offsets)

    assert in_x == pytest.approx(expected[0])
    assert in_y == pytest.approx(expected[1])
    assert out_x == pytest.approx(expected[2])
    assert out_y == pytest.approx(expected[3])
