# Posit SDK for Python

This package provides a Pythonic interface for developers to work against the public APIs of Posit's professional products. It is intended to be lightweight yet expressive.

> The Posit SDK is in the very early stages of development, and currently only Posit Connect has any support.

## Installation

```shell
pip install posit-sdk
```

## Usage

```python
from posit.connect import Client

# If CONNECT_API_KEY and CONNECT_SERVER are set in your environment,
# they will be picked up, or you can pass them as arguments
con = Client()
con.users.find()
```

## Contributing

We welcome contributions to the Posit SDK for Python! If you would like to contribute, see the [CONTRIBUTING](CONTRIBUTING.md) guide for instructions.

## Issues

If you encounter any issues or have any questions, please [open an issue](https://github.com/posit-dev/posit-sdk-py/issues). We appreciate your feedback.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you see fit.

## Code of Conduct

We expect all contributors to adhere to the project's [Code of Conduct](CODE_OF_CONDUCT.md) and create a positive and inclusive community.
