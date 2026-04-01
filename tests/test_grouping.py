from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.grouping import order_geo


def test_order_geo_prefer_x():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 0, 30, 5, 30),
        PathBBox(3, 40, 0, 50, 5, 30),
    ]

    ordered, bands = order_geo(paths, prefer_y=False)

    assert ordered == [1, 2, 3]
    assert isinstance(bands, tuple)


def test_order_geo_prefer_y():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 0, 20, 10, 25, 30),
        PathBBox(3, 0, 40, 10, 45, 30),
    ]

    ordered, bands = order_geo(paths, prefer_y=True)

    assert ordered == [1, 2, 3]
    assert isinstance(bands, tuple)


def test_order_geo_empty():
    ordered, bands = order_geo([], prefer_y=False)
    assert ordered == []
    assert bands == (0, 0)


def test_order_geo_same_x_band():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),  # width = 10 → delta_x = 8
        PathBBox(2, 5, 10, 15, 15, 30),  # x=5 is within ±8 of x=0
        PathBBox(3, 7, 20, 17, 25, 30),  # x=7 also within band
    ]

    ordered, bands = order_geo(paths, prefer_y=False)

    assert ordered == [1, 2, 3]
    assert isinstance(bands, tuple)


def test_order_geo_two_x_bands():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 7, 10, 17, 15, 30),
        PathBBox(3, 30, 0, 40, 5, 30),
    ]

    ordered, bands = order_geo(paths, prefer_y=False)

    # All items must appear exactly once
    assert sorted(ordered) == [1, 2, 3]

    # First band contains 2 items (1 and 2)
    assert bands[0] == 2


def test_order_geo_y_bands():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 0, 7, 10, 12, 30),
        PathBBox(3, 0, 20, 10, 25, 30),
    ]

    ordered, bands = order_geo(paths, prefer_y=True)

    # All items appear exactly once
    assert sorted(ordered) == [1, 2, 3]

    # The algorithm groups all 3 into the first band after the second pass
    assert bands[0] == 3


def test_order_geo_identical_coords():
    paths = [
        PathBBox(1, 10, 10, 20, 20, 30),
        PathBBox(2, 10, 10, 20, 20, 30),
        PathBBox(3, 10, 10, 20, 20, 30),
    ]

    ordered, _ = order_geo(paths, prefer_y=False)
    assert ordered == [1, 2, 3]


def test_order_geo_mixed_xy():
    paths = [
        PathBBox(1, 0, 50, 10, 55, 30),
        PathBBox(2, 0, 10, 10, 15, 30),
        PathBBox(3, 0, 30, 10, 35, 30),
    ]

    ordered, _ = order_geo(paths, prefer_y=False)

    # All X are equal → sorted by Y
    assert ordered == [2, 3, 1]


def test_order_geo_mixed_xy_prefer_y():
    paths = [
        PathBBox(1, 50, 0, 60, 5, 30),
        PathBBox(2, 10, 0, 20, 5, 30),
        PathBBox(3, 30, 0, 40, 5, 30),
    ]

    ordered, _ = order_geo(paths, prefer_y=True)

    # All Y equal → sorted by X
    assert ordered == [2, 3, 1]
