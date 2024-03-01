import requests
import responses

from unittest.mock import MagicMock

from .paginator import Paginator

class TestPaginator:

    @responses.activate
    def test_iter(self):
        session = requests.Session()
        page_size = 10
        paginator = Paginator(session=session, url="http://foo.bar/__api__", page_size=page_size)
        assert paginator == iter(paginator)
        assert paginator.index == 0

    def test_next_single_page(self):
        pass

    def test_next_with_multiple_pages(self):
        pass

    def test_len(self):
        pass
