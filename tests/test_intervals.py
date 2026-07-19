from ctoverlap.intervals import trial_interval
from datetime import date

def test_missing_start():
    test_date = {
        "start date": "",
        "completion date": "August 22, 2006",
        "primary completion date": "",
        "overall trial status": "completed",
        "extraction date": "2026-07-18T12:00:00"
    }

    result = trial_interval(test_date)
    expected = (
    None,
    None,
    "missing",
    False,
    "missing_start_date"
    )

    assert result == expected, f"Result: {result} Expected: {expected}"



def test_missing_end():
    test_date = {
        "start date": "August 22, 2006",
        "completion date": "",
        "primary completion date": "",
        "overall trial status": "completed",
        "extraction date": "2026-07-18T12:00:00"
    }

    result = trial_interval(test_date)
    expected = (
        date(2006, 8, 22),
        None,
        "missing",
        False,
        "missing_end_date_for_closed_trial"
        )

    assert result == expected, f"Result: {result} Expected: {expected}"

def test_primary_fallback():
    test_date = {
        "start date": "August 22, 2006",
        "completion date": "",
        "primary completion date": "August 22, 2008",
        "overall trial status": "completed",
        "extraction date": "2026-07-18T12:00:00"
    }

    result = trial_interval(test_date)
    expected = (
        date(2006, 8, 22),
        date(2008, 8, 22),
        "primary_completion_date",
        True,
        None
    )

    assert result == expected, f"Result: {result} Expected: {expected}"


def test_ongoing_trial():
    test_date = {
        "start date": "August 22, 2006",
        "completion date": "",
        "primary completion date": "",
        "overall trial status": "recruiting",
        "extraction date": "2026-07-18T12:00:00"
    }

    result = trial_interval(test_date)
    expected = (
        date(2006, 8, 22),
        date(2026, 7, 18),
        "extraction_date_for_ongoing_trial",
        True,
        None
    )

    assert result == expected, f"Result: {result} Expected: {expected}"
