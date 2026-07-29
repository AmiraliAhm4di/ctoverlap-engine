from ctoverlap.sweep_line import sweep_line
from ctoverlap.brute_force import brute_force


def test_sweep_line_matches_brute_force():
    test_intervals = [
        ("2020-01", "2020-03"),
        ("2020-02", "2020-04"),
        ("2020-03", "2020-03"),
    ]

    sweep_result = sweep_line(test_intervals)
    brute_result = brute_force(test_intervals)

    sweep_timeline = sweep_result[2]

    assert sweep_timeline == brute_result