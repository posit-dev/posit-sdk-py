import os

from posit.connect import config


def pytest_configure():
    c = config.Config()
    c.api_key = "12345"
    c.url = "https://connect.example/__api__"
