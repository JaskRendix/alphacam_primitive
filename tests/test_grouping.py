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
