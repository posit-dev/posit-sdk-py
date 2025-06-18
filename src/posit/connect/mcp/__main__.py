import click

from .server import run_stdio_server, run_streamable_http_server


@click.group()
def run():
    pass


@click.command()
def stdio():
    run_stdio_server()


@click.command()
@click.argument("--host", default="127.0.0.1")
@click.argument("--port", default=8001)
def http(host: str, port: int):
    run_streamable_http_server(host, port)


run.add_command(stdio)
run.add_command(http)

if __name__ == "__main__":
    run()
