---
layout: default
title: Running Examples
permalink: /docs/running-examples.html
nav_order: 2
---

# Running These Examples

All of the examples given in these docs are designed without any additional dependencies or infrastructure.  For instance, they use the memory backend instead of the database backend so you don't need to have a database around to run them (unless, of course, the example shows how to interact with other systems).  Therefore, you should be able to run all the examples in here with minimal effort.  There are two kinds of applications used in these examples, and so here are instructions for how to run them:

 1. [Examples run via the CLI](#running-examples-designed-for-the-cli)
 2. [Examples called by an HTTP server](#running-examples-designed-for-an-http-server)

### Running Examples Designed for the CLI

Some of the examples are designed to be run directly from the command line.  In this case, you have a variety of options.  The simplest is to just install clearskies:

```
pip install clear-skies
```

(or use pipenv/poetry if preferred).  Then you can copy and paste the example code into a local file (e.g. `clearskies_example.py`) and add the appropriate shebang (e.g. `#!`) to the top of the file to point to your python distribution.  That typically looks like:

```
#!/usr/bin/env python
# the rest of the code here
```

then you add execution permission to the file (`chmod u+x clearskies_example.py`) and can execute it directly:

```
./clearskies_example.py
```

If you're using poetry you can try a different variation:

```
poetry run python clearskies_example.py
```

for the above, you don't need the shebang nor do you have to add execution permission to the file.

### Running Examples Designed for an HTTP Server

Many of these examples are designed to called from an HTTP server.  clearskies doesn't ship with one by default because python relies heavily on the WSGI standard. which clearskies supports.  Therefore, all the HTTP-focused examples in these docs are intended to be consumed by a WSGI server.  If you don't already have one you like, then the simplest way to get started is with [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html).  Installing it is usually as simple as:

```
pip install uwsgi
```

To run the examples in these docs, you then copy and paste the given code into a local python file (e.g. `clearskies_example.py`) and then tell uwsgi to run it:

```
uwsgi --http :9090 --wsgi-file clearskies_example.py
```

This will start up a local server on port 9090 that hosts the application.  You can then interact with it via curl/postman/whatever:

```
curl http://localhost:9090
```

The examples always come with example curl commands to execute the application, so just follow along with those once you have your local server running.
