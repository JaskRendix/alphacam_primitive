from alphacam_primitive.geometry import GeoRecord, PathBBox


def test_pathbbox_properties():
    p = PathBBox(
        name=1,
        min_x=0,
        min_y=0,
        max_x=10,
        max_y=5,
        length=30,
    )

    assert p.width == 10
    assert p.height == 5
    assert p.length == 30


def test_georecord_basic():
    r = GeoRecord(ind=1, name=7, x=3.5, y=9.2)

    assert r.ind == 1
    assert r.name == 7
    assert r.x == 3.5
    assert r.y == 9.2
