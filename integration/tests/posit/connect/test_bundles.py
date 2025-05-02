import time
from pathlib import Path

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


class TestBundles:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(
            name=f"test-bundles-{int(time.time())}",
            title="Test Bundles",
            access_type="all",
        )
        # Path to the test bundle
        bundle_path = Path(
            "../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz"
        )
        cls.bundle_path = (Path(__file__).parent / bundle_path).resolve()

    @classmethod
    def teardown_class(cls):
        cls.content.delete()

    def test_create_bundle(self):
        """Test creating a bundle."""
        bundle = self.content.bundles.create(str(self.bundle_path))
        assert bundle["id"]
        assert bundle["content_guid"] == self.content["guid"]

    def test_find_bundles(self):
        """Test finding all bundles."""
        # Create a bundle first
        self.content.bundles.create(str(self.bundle_path))

        # Find all bundles
        bundles = self.content.bundles.find()
        assert len(bundles) >= 1

    def test_find_one_bundle(self):
        """Test finding a single bundle."""
        # Create a bundle first
        self.content.bundles.create(str(self.bundle_path))

        # Find one bundle
        bundle = self.content.bundles.find_one()
        assert bundle is not None
        assert bundle["content_guid"] == self.content["guid"]

    def test_get_bundle(self):
        """Test getting a specific bundle."""
        # Create a bundle first
        created_bundle = self.content.bundles.create(str(self.bundle_path))

        # Get the bundle by ID
        bundle = self.content.bundles.get(created_bundle["id"])
        assert bundle["id"] == created_bundle["id"]

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.02.0"), reason="Requires Connect 2025.02.0 or later"
    )
    def test_active_bundle(self):
        """Test retrieving the active bundle."""
        # Initially, no bundle should be active
        assert self.content.bundles.active() is None

        # Create and deploy a bundle
        bundle = self.content.bundles.create(str(self.bundle_path))
        task = bundle.deploy()
        task.wait_for()

        # Wait for the bundle to become active
        max_retries = 10
        active_bundle = None
        for _ in range(max_retries):
            active_bundle = self.content.bundles.active()
            if active_bundle is not None:
                break
            time.sleep(1)

        # Verify the bundle is now active
        assert active_bundle is not None
        assert active_bundle["id"] == bundle["id"]
        assert active_bundle.get("active") is True

        # Create another bundle but don't deploy it
        bundle2 = self.content.bundles.create(str(self.bundle_path))

        # Verify the active bundle is still the first one
        active_bundle = self.content.bundles.active()
        assert active_bundle is not None
        assert active_bundle["id"] == bundle["id"]
        assert active_bundle["id"] != bundle2["id"]
