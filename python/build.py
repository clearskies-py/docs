import json

import clearskies
import app

config_file = open("config.json", "r")
config = json.loads(config_file.read())
config_file.close()


cli = clearskies.contexts.Cli(
    app.app,
    modules=[app.models, app.backends],
)
cli()
