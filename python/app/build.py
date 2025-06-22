import clearskies
from app import models

def build(modules: models.Module, classes: models.Class):
    endpoints = modules.find("import_path=clearskies.endpoints")
    for endpoint in endpoints.classes:
        print(endpoint.name)
        print(endpoint.doc)
        print(endpoint.init.args)
