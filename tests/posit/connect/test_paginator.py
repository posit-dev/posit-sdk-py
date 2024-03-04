import pytest

from unittest.mock import MagicMock, patch


from posit.connect.paginator import Paginator


@pytest.fixture
def mock_session():
    with patch("posit.connect.paginator.requests.Session") as mock:
        yield mock()


class TestPaginator:
    def test_iter(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 10
        paginator = Paginator(mock_session, url, page_size=page_size)
        assert paginator == iter(paginator)
        assert paginator.index == 0

    def test_fetch(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 10
        paginator = Paginator(mock_session, url, page_size=page_size)
        mock_session.get.return_value.json.return_value = {"results": [{"foo": "bar"}]}
        results, exhausted = paginator.fetch(1)
        assert results == [{"foo": "bar"}]
        assert exhausted

    def test_fetch_with_value_error(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 10
        paginator = Paginator(mock_session, url, page_size=page_size)
        with pytest.raises(ValueError):
            paginator.fetch(0)

    def test_len(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 1
        paginator = Paginator(mock_session, url, page_size=page_size)
        mock_session.get.return_value.json.return_value = {"total": "24"}
        assert len(paginator) == 24
        mock_session.get.assert_called_once_with(
            url, params={"page_number": 1, "page_size": 1}
        )

    def test_next(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 1
        paginator = Paginator(mock_session, url, page_size=page_size)
        paginator.elements = [{"foo": "bar"}]
        paginator.index = 0
        assert next(paginator) == {"foo": "bar"}
        assert paginator.index == 1

    def test_next_with_fetch(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 1
        paginator = Paginator(mock_session, url, page_size=page_size)
        mock_session.get.return_value.json.return_value = {"results": [{"foo": "bar"}]}
        paginator.index = 0
        assert next(paginator) == {"foo": "bar"}
        assert paginator.index == 1

    def test_next_with_fetch_with_no_results(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 1
        paginator = Paginator(mock_session, url, page_size=page_size)
        mock_session.get.return_value.json.return_value = {"results": []}
        paginator.index = 0
        with pytest.raises(StopIteration):
            next(paginator)

    def test_next_when_exhausted(self, mock_session: MagicMock):
        url = "http://foo.bar/__api__"
        page_size = 1
        paginator = Paginator(mock_session, url, page_size=page_size)
        paginator.exhausted = True
        with pytest.raises(StopIteration):
            next(paginator)
