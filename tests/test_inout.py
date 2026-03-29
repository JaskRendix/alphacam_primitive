from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.inout import InOutOffsets, compute_inout_points


def test_compute_inout_points():
    p = PathBBox(1, 0, 0, 10, 5, 30)
    offsets = InOutOffsets(in_dx=1, in_dy=2, out_dx=3, out_dy=4)

    in_x, in_y, out_x, out_y = compute_inout_points(p, offsets)

    assert in_x == 9
    assert in_y == 3
    assert out_x == 7
    assert out_y == 1
