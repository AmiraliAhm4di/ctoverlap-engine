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


def test_empty_intervals():
    assert sweep_line([]) == (0, {}, {})
    assert brute_force([]) == {}


def test_overlap_across_new_year():
    intervals = [("2020-12", "2021-01"), ("2021-01", "2021-01")]
    expected = {"2020-12": 1, "2021-01": 2}
    assert sweep_line(intervals)[2] == expected
    assert brute_force(intervals) == expected
