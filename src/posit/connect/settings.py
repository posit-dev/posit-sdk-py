from typing import Optional

import requests

from .urls import Url


class Settings:
    def __init__(self, session: requests.Session, url: Url) -> None:
        self.session = session
        self.url = url

    @property
    def version(self) -> Optional[str]:
        return self.settings.get("version")

    @property
    def settings(self) -> dict:
        url = self.url + "server_settings"
        try:
            response = self.session.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            import logging

            logging.debug(
                f"Failed to retrieve server settings from {url}. Error: {str(e)}", exc_info=True
            )

            return {}
