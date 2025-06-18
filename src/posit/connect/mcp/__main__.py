import click

from .server import get_streamable_http_server, run_stdio_server


@click.group()
def run():
    pass


@click.command()
def stdio():
    run_stdio_server()


@click.command()
def http():
    app = get_streamable_http_server()
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)


run.add_command(stdio)
run.add_command(http)

if __name__ == "__main__":
    run()
