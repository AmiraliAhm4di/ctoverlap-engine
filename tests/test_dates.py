from ctoverlap.dates import parse_trial_date
from datetime import date

def test_format():
    test_date = "August 22, 2006"
    result = parse_trial_date(test_date)
    expected = date(2006, 8, 22)

    assert result == expected, f"Result: {result} Expected: {expected}"

def test_missing_value():
    test_date = ""
    result = parse_trial_date(test_date)
    expected = None

    assert result == expected, f"Result: {result} Expected: {expected}"
