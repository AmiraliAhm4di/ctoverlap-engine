import subprocess
from unittest.mock import Mock
import pytest
from ctoverlap.report import run_report


def test_missing_r_returns_failure(monkeypatch):
    monkeypatch.setattr("ctoverlap.report.shutil.which", lambda name: None)
    with pytest.raises(SystemExit) as error:
        run_report()
    assert error.value.code == 1


def test_missing_report_script_returns_failure(monkeypatch, tmp_path):
    monkeypatch.setattr("ctoverlap.report.shutil.which", lambda name: "Rscript")
    monkeypatch.setattr("ctoverlap.report.REPORT_SCRIPT", tmp_path / "missing.R")
    with pytest.raises(SystemExit) as error:
        run_report()
    assert error.value.code == 1


def test_r_failure_returns_failure(monkeypatch):
    monkeypatch.setattr("ctoverlap.report.shutil.which", lambda name: "Rscript")
    monkeypatch.setattr("ctoverlap.report.subprocess.run", Mock(side_effect=subprocess.CalledProcessError(1, "Rscript")))
    with pytest.raises(SystemExit) as error:
        run_report()
    assert error.value.code == 1
