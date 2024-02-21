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

<!-- Add notes about local development -->

<!-- Add code of conduct -->