import pytest
import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.variants import Variant

from .api import load_mock


class TestVariantSendMail:
    @responses.activate
    def test_send_mail_to_me(self):
        """Test sending email to 'me'."""
        variant_id = 6627
        rendering_id = 3055012

        # Mock the send_mail endpoint
        post_sender = responses.post(
            f"https://connect.example.com/__api__/variants/{variant_id}/sender",
            match=[
                matchers.query_param_matcher(
                    {"email": "me", "rendering_id": rendering_id}
                )
            ],
            json=load_mock(f"variants/{variant_id}/sender.json"),
        )

        # Setup
        c = Client("https://connect.example.com", "12345")
        variant = Variant(
            c._ctx,
            id=variant_id,
            rendering_id=rendering_id,
            app_id=50941,
            key="txvRW8SG",
            bundle_id=120726,
            is_default=True,
            name="default",
        )

        # Invoke
        with pytest.warns(FutureWarning, match="send_mail.*experimental"):
            task = variant.send_mail(to="me")

        # Assert
        assert task is not None
        assert task["id"] == "jXhOhdm5OOSkMail"
        assert task["finished"] is True
        assert task["code"] == 0
        assert post_sender.call_count == 1

    @responses.activate
    def test_send_mail_to_collaborators(self):
        """Test sending email to 'collaborators'."""
        variant_id = 6627
        rendering_id = 3055012

        # Mock the send_mail endpoint
        post_sender = responses.post(
            f"https://connect.example.com/__api__/variants/{variant_id}/sender",
            match=[
                matchers.query_param_matcher(
                    {"email": "collaborators", "rendering_id": rendering_id}
                )
            ],
            json=load_mock(f"variants/{variant_id}/sender.json"),
        )

        # Setup
        c = Client("https://connect.example.com", "12345")
        variant = Variant(
            c._ctx,
            id=variant_id,
            rendering_id=rendering_id,
            app_id=50941,
            key="txvRW8SG",
            bundle_id=120726,
            is_default=True,
            name="default",
        )

        # Invoke
        with pytest.warns(FutureWarning, match="send_mail.*experimental"):
            task = variant.send_mail(to="collaborators")

        # Assert
        assert task is not None
        assert post_sender.call_count == 1

    @responses.activate
    def test_send_mail_to_collaborators_viewers(self):
        """Test sending email to 'collaborators_viewers'."""
        variant_id = 6627
        rendering_id = 3055012

        # Mock the send_mail endpoint
        post_sender = responses.post(
            f"https://connect.example.com/__api__/variants/{variant_id}/sender",
            match=[
                matchers.query_param_matcher(
                    {"email": "collaborators_viewers", "rendering_id": rendering_id}
                )
            ],
            json=load_mock(f"variants/{variant_id}/sender.json"),
        )

        # Setup
        c = Client("https://connect.example.com", "12345")
        variant = Variant(
            c._ctx,
            id=variant_id,
            rendering_id=rendering_id,
            app_id=50941,
            key="txvRW8SG",
            bundle_id=120726,
            is_default=True,
            name="default",
        )

        # Invoke
        with pytest.warns(FutureWarning, match="send_mail.*experimental"):
            task = variant.send_mail(to="collaborators_viewers")

        # Assert
        assert task is not None
        assert post_sender.call_count == 1

    @responses.activate
    def test_send_mail_default_to_me(self):
        """Test that send_mail defaults to 'me' when no parameter provided."""
        variant_id = 6627
        rendering_id = 3055012

        # Mock the send_mail endpoint
        post_sender = responses.post(
            f"https://connect.example.com/__api__/variants/{variant_id}/sender",
            match=[
                matchers.query_param_matcher(
                    {"email": "me", "rendering_id": rendering_id}
                )
            ],
            json=load_mock(f"variants/{variant_id}/sender.json"),
        )

        # Setup
        c = Client("https://connect.example.com", "12345")
        variant = Variant(
            c._ctx,
            id=variant_id,
            rendering_id=rendering_id,
            app_id=50941,
            key="txvRW8SG",
            bundle_id=120726,
            is_default=True,
            name="default",
        )

        # Invoke - no 'to' parameter specified
        with pytest.warns(FutureWarning, match="send_mail.*experimental"):
            task = variant.send_mail()

        # Assert
        assert task is not None
        assert post_sender.call_count == 1
