import time
from pathlib import Path

import pytest
import requests
from packaging import version

from posit import connect
from posit.connect.content import ContentItem

from .. import CONNECT_VERSION

BUNDLE_PATH = (
    Path(__file__).parent
    / "../../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz"
).resolve()


@pytest.mark.skipif(
    CONNECT_VERSION < version.parse("2026.01.0"),
    reason="content_guid filter on hits API requires Connect 2026.01.0+",
)
class TestHitsContentGuidFilter:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()

        # Deploy two content items and visit them to generate hits.
        cls.content_a = cls._deploy("hits_filter_a")
        cls.content_b = cls._deploy("hits_filter_b")

        # Visit each piece of content to generate hit records.
        cls._visit(cls.content_a)
        cls._visit(cls.content_b)

        # The hits endpoint may not surface records immediately.
        # Poll until hits for both content items appear (up to 10 s).
        guid_a = cls.content_a["guid"]
        guid_b = cls.content_b["guid"]
        deadline = time.time() + 10
        while time.time() < deadline:
            all_hits = list(cls.client.metrics.hits.fetch())
            guids = {h["content_guid"] for h in all_hits}
            if guid_a in guids and guid_b in guids:
                break
            time.sleep(0.5)

    @classmethod
    def teardown_class(cls):
        cls.content_a.delete()
        cls.content_b.delete()

    @classmethod
    def _deploy(cls, name: str) -> ContentItem:
        content = cls.client.content.create(name=name)
        bundle = content.bundles.create(str(BUNDLE_PATH))
        task = bundle.deploy()
        task.wait_for()
        return content

    @classmethod
    def _visit(cls, content: ContentItem) -> None:
        """Make an HTTP request to deployed content to generate a hit."""
        # Re-fetch the content item to get the content_url populated after deploy.
        item = cls.client.content.get(content["guid"])
        url = item["content_url"]
        api_key = cls.client.cfg.api_key
        requests.get(url, headers={"Authorization": f"Key {api_key}"})

    # -- tests ----------------------------------------------------------------

    def test_fetch_all_includes_both(self):
        """Unfiltered fetch returns hits for both deployed content items."""
        all_hits = list(self.client.metrics.hits.fetch())
        guids = {h["content_guid"] for h in all_hits}
        assert self.content_a["guid"] in guids
        assert self.content_b["guid"] in guids

    def test_fetch_with_single_content_guid(self):
        """Filtering by a single GUID returns only hits for that content."""
        guid_a = self.content_a["guid"]
        hits = list(self.client.metrics.hits.fetch(content_guid=guid_a))
        assert len(hits) > 0
        for hit in hits:
            assert hit["content_guid"] == guid_a

    def test_fetch_with_content_guid_list(self):
        """Filtering by a list of GUIDs returns only hits for those items."""
        guid_a = self.content_a["guid"]
        guid_b = self.content_b["guid"]
        hits = list(self.client.metrics.hits.fetch(content_guid=[guid_a, guid_b]))
        assert len(hits) > 0
        for hit in hits:
            assert hit["content_guid"] in (guid_a, guid_b)

    def test_fetch_with_content_guid_excludes_other(self):
        """Filtering by content_a's GUID does not return content_b's hits."""
        guid_a = self.content_a["guid"]
        guid_b = self.content_b["guid"]
        hits = list(self.client.metrics.hits.fetch(content_guid=guid_a))
        hit_guids = {h["content_guid"] for h in hits}
        assert guid_a in hit_guids
        assert guid_b not in hit_guids

    def test_fetch_with_content_guid_no_match(self):
        """Filtering by a non-existent GUID returns no results."""
        hits = list(
            self.client.metrics.hits.fetch(content_guid="00000000-0000-0000-0000-000000000000")
        )
        assert hits == []

    def test_fetch_filtered_is_subset_of_unfiltered(self):
        """Filtered results are a strict subset of unfiltered results."""
        guid_a = self.content_a["guid"]
        all_hits = list(self.client.metrics.hits.fetch())
        filtered_hits = list(self.client.metrics.hits.fetch(content_guid=guid_a))
        all_ids = {h["id"] for h in all_hits}
        filtered_ids = {h["id"] for h in filtered_hits}
        assert filtered_ids <= all_ids
        assert len(filtered_ids) < len(all_ids)
