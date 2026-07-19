from ctoverlap.phases import phase_cleaner

def test_format():
    test_date = "PHASE4"
    result = phase_cleaner(test_date)
    expected = "Phase 4"

    assert result == expected, f"Result: {result} Expected: {expected}"

def test_format_2():
    test_date = ["PHASE1", "PHASE2"]
    result = phase_cleaner(test_date)
    expected = "Phase 1/2"

    assert result == expected, f"Result: {result} Expected: {expected}"

def test_missing_value():
    test_date = ""
    result = phase_cleaner(test_date)
    expected = "Unspecified / Not Applicable"

    assert result == expected, f"Result: {result} Expected: {expected}"