import csv
from ctoverlap.clean import save_cleaned


def test_save_cleaned_without_excluded_trials(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    row = {"NCT ID": "NCT00000001", "overlap_eligible": True}
    monkeypatch.setattr("ctoverlap.clean.clean_all", lambda: ([row], []))
    save_cleaned()
    with (tmp_path / "data/processed/excluded_trials.csv").open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == list(row)
        assert list(reader) == []
