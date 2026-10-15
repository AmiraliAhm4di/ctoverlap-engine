from unittest.mock import Mock
from ctoverlap.download import fetch_studies


def test_download_returns_records_and_keeps_limit(monkeypatch):
    for record_count, next_token in [(0, None), (1, None), (1000, "next")]:
        studies = [{"id": str(i)} for i in range(record_count)]
        response = Mock()
        response.json.return_value = {"studies": studies, "totalCount": 2000, "nextPageToken": next_token}
        request = Mock(return_value=response)
        monkeypatch.setattr("ctoverlap.download.requests.get", request)
        assert fetch_studies("melanoma") == {"studies": studies, "totalCount": 2000}
        request.assert_called_once()
        response.raise_for_status.assert_called_once()


def test_download_does_not_exceed_limit_across_pages(monkeypatch):
    first_page = Mock()
    first_page.json.return_value = {"studies": [{"id": "first"}] * 999, "nextPageToken": "next", "totalCount": 2000}
    second_page = Mock()
    second_page.json.return_value = {"studies": [{"id": "last"}, {"id": "extra"}], "totalCount": 2000}
    request = Mock(side_effect=[first_page, second_page])
    monkeypatch.setattr("ctoverlap.download.requests.get", request)
    result = fetch_studies("melanoma")
    assert len(result["studies"]) == 1000
    assert result["studies"][-1] == {"id": "last"}
    assert request.call_args_list[1].kwargs["params"]["pageToken"] == "next"
