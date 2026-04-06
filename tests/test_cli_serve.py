import argparse

import alphacam_primitive.cli as cli


def test_cli_serve(monkeypatch):
    called = {}

    def fake_run(app, host, port, reload):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["reload"] = reload

    monkeypatch.setattr(cli, "uvicorn", type("Uvicorn", (), {"run": fake_run}))

    args = argparse.Namespace(
        host="0.0.0.0",
        port=9000,
        reload=False,
        func=cli.cmd_serve,
    )

    cli.cmd_serve(args)

    assert called["app"] == "alphacam_primitive.api:app"
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 9000
    assert called["reload"] is False
