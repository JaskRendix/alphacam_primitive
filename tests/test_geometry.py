import pytest

from alphacam_primitive.geometry import GeoRecord, PathBBox, from_paths


def test_pathbbox_basic_properties():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    assert p.width == 10
    assert p.height == 5
    assert p.length == 30


def test_pathbbox_negative_coordinates():
    p = PathBBox(1, -10, -5, 10, 5, 0)
    assert p.width == 20
    assert p.height == 10


def test_pathbbox_zero_size():
    p = PathBBox(1, 5, 5, 5, 5, 0)
    assert p.width == 0
    assert p.height == 0


def test_pathbbox_float_precision():
    p = PathBBox(1, 0.1, 0.2, 10.3, 5.7, 0)
    assert p.width == pytest.approx(10.2)
    assert p.height == pytest.approx(5.5)


def test_pathbbox_min_greater_than_max():
    # Not physically meaningful, but should still compute width/height consistently
    p = PathBBox(1, 10, 10, 0, 0, 0)
    assert p.width == -10
    assert p.height == -10


def test_georecord_basic_fields():
    r = GeoRecord(ind=1, name=7, x=3.5, y=9.2)
    assert r.ind == 1
    assert r.name == 7
    assert r.x == 3.5
    assert r.y == 9.2


def test_georecord_allows_zero_and_negative():
    r = GeoRecord(ind=0, name=-5, x=-10.0, y=0.0)
    assert r.ind == 0
    assert r.name == -5
    assert r.x == -10.0
    assert r.y == 0.0


def test_georecord_sorting_behavior():
    records = [
        GeoRecord(3, 10, 5, 5),
        GeoRecord(1, 20, 1, 1),
        GeoRecord(2, 30, 3, 3),
    ]
    sorted_records = sorted(records, key=lambda r: r.ind)
    assert [r.ind for r in sorted_records] == [1, 2, 3]


def test_from_paths_list_passthrough():
    paths = [
        PathBBox(1, 0, 0, 1, 1, 0),
        PathBBox(2, 1, 1, 2, 2, 0),
    ]
    out = from_paths(paths)
    assert out == paths  # same objects
    assert isinstance(out, list)


def test_from_paths_generator():
    gen = (PathBBox(i, 0, 0, 1, 1, 0) for i in range(3))
    out = from_paths(gen)
    assert len(out) == 3
    assert all(isinstance(p, PathBBox) for p in out)


def test_from_paths_empty():
    out = from_paths([])
    assert out == []
