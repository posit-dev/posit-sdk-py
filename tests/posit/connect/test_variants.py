import pytest
import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.variants import Variant, Variants

from .api import load_mock


class TestVariantSendMail:
    @pytest.mark.parametrize(
        ("to", "expected_email"),
        [
            ("me", "me"),
            ("collaborators", "collaborators"),
            ("collaborators_viewers", "collaborators_viewers"),
            (None, "me"),  # default value
        ],
    )
    @responses.activate
    def test_basic_send_mail(self, to, expected_email):
        variant_id = 6627
        rendering_id = 3055012

        mock_post = responses.post(
            f"https://connect.example.com/__api__/variants/{variant_id}/sender",
            match=[
                matchers.query_param_matcher(
                    {"email": expected_email, "rendering_id": rendering_id}
                )
            ],
            json=load_mock(f"variants/{variant_id}/sender.json"),
        )

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

        kwargs = {} if to is None else {"to": to}
        with pytest.warns(FutureWarning, match="send_mail.*experimental"):
            task = variant.send_mail(**kwargs)

        assert task["id"] == "jXhOhdm5OOSkMail"
        assert task["finished"] is True
        assert task["code"] == 0
        assert mock_post.call_count == 1
