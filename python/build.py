import json
import pathlib

import clearskies
import app

config_file = open("config.json", "r")
config = json.loads(config_file.read())
config_file.close()

project_root = str(pathlib.Path(__file__).parents[1])

cli = clearskies.contexts.Cli(
    app.app,
    modules=[app.models, app.backends],
    bindings={
        "config": config,
        "project_root": project_root,
    },
)
cli()
