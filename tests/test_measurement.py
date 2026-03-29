from alphacam_primitive.geometry import PathBBox
from alphacam_primitive.measurement import compute_measurement_points


def test_compute_measurement_points():
    paths = [
        PathBBox(1, 0, 0, 10, 5, 30),
        PathBBox(2, 20, 0, 30, 5, 30),
        PathBBox(3, 40, 0, 50, 5, 30),
    ]

    ordered = [1, 2, 3]

    measurement, count_g = compute_measurement_points(
        paths=paths,
        ordered_indices=ordered,
        geo_min=0,
        geo_max=60,
        count_per_band=3,
        delta_measure=1.0,
        prefer_y=False,
    )

    assert len(measurement) == 3
    assert count_g == [1, 2, 3]

    # Check first measurement point
    m1 = measurement[1]
    assert m1.x == 1.0
    assert m1.y == 0.0
