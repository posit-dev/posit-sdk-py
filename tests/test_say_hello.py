from unittest.mock import patch

from posit.say_hello import say_hello


def test_say_hello():
    with patch("builtins.print") as mock_print:
        say_hello("World")
        mock_print.assert_called_once_with("Hello, World!")
