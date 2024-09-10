# Posit SDK for Python

This package provides a Pythonic interface for developers to work against the public APIs of Posit's professional products. It is intended to be lightweight yet expressive.

> The Posit SDK is in the very early stages of development, and currently only Posit Connect has any support.

## Installation

```shell
pip install posit-sdk
```

## Usage

Establish server information and credentials using the following environment variables or when initializing a client. Then checkout the [Posit Connect Cookbook](https://docs.posit.co/connect/cookbook/) to get started.

> [!CAUTION]
> It is important to keep your API key safe and secure. Your API key grants access to your account and allows you to make authenticated requests to the Posit API. Treat your API key like a password and avoid sharing it with others. If you suspect that your API key has been compromised, regenerate a new one immediately to maintain the security of your account.

### Option 1 (Preferred)

```shell
export CONNECT_API_KEY="my-secret-api-key"
export CONNECT_SERVER="https://example.com/"
```

```python
from posit.connect import Client

client = Client()
```

### Option 2

```shell
export CONNECT_API_KEY="my-secret-api-key"
```

```python
from posit.connect import Client

Client("https://example.com")
```

### Option 3

```python
from posit.connect import Client

Client("https://example.com", "my-secret-api-key")
```

## Contributing

We welcome contributions to the Posit SDK for Python! If you would like to contribute, see the [CONTRIBUTING](CONTRIBUTING.md) guide for instructions.

## Issues

If you encounter any issues or have any questions, please [open an issue](https://github.com/posit-dev/posit-sdk-py/issues). We appreciate your feedback.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you see fit.

## Code of Conduct

We expect all contributors to adhere to the project's [Code of Conduct](CODE_OF_CONDUCT.md) and create a positive and inclusive community.
