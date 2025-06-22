---
layout: default
title: Callable
parent: Handlers
permalink: /docs/handlers/callable.html
nav_order: 3
---

# Callable Handler

 1. [Overview](#overview)
 2. [Configuration](#configuration)

## Overview

The callable handler is the most basic handler, and all it does is invoke a function.  You may request any dependencies that exist in your application, and you may also request any of the additional call-specific dependencies:

| Name | Value |
|------|-------|
| `input_output` | An instance of `clearskies.input_output.InputOutput` - used to check the request and modify the response |
| `request_data` | The data in the request, if present |
| [Routing Data](#simple-routing.html) | Any routing data present.  The injection name varies - see the [simple router](simple-routing.html) for more information |

## Configuration

| Name | Type | Description |
|------|------|-------------|
| [callable](#callable) | `Callable` | The callable to execute - a function, lambda, or object with a `__call__` attribute. |
| [return_raw_response](#return-raw-response) | `bool` | If `True`, the return value of the callable will returned exactly to the client.  If not, it will be set as the `data` property of a standard clearskies response |
| [schema](#schema) | List of columns OR Model class OR Model | A schema to use to validate user input |
| [writeable_columns](#writeable-columns) | `List[str]` | A list of column names (from the schema) that the user is allowed to set |
| [doc_model_name](#doc-model-name) | `str` | The name to assign to the response type for use in the autodocumentation of the handler |
| [doc_response_data_schema](#doc-response-data-schema) | `List[clearskies.autodoc.schema.base]` | The documentation of the response for the handler for use in the autodocs |

### Callable

The callable to execute.  That's... really all there is to it.  Since the callable is the default handler, it's possible to attach it directly to a context without having to specify a handler class or handler config:

{% highlight python %}
#!/usr/bin/env python
import clearskies

def example_callable(test_binding):
    return f'Hello {test_binding}'

callable_demo = clearskies.contexts.cli(
    example_callable,
    bindings={
        'test_binding': 'world',
    }
)
callable_demo()
{% endhighlight %}

The above example can be [executed via the CLI](/docs/running-examples.html#running-examples-designed-for-the-cli).  Of course, the CLI handler works just as well in a web context.  However, a web context requires you to specify the authenticaton method.  To help with this, there are decorators for every configuration option in the callable handler:

{% highlight python %}
import clearskies

@clearskies.decorators.public()
def example_callable(test_binding):
    return f'Hello {test_binding}'

callable_demo = clearskies.contexts.wsgi(
    example_callable,
    bindings={
        'test_binding': 'world',
    }
)
def application(env, start_response):
    return callable_demo(env, start_response)
{% endhighlight %}

[Run this in a local server](docs/running-examples.html#running-examples-designed-for-an-http-server) and then invoke it via something like curl:

```
curl 'http://localhost:9090'
```

and you'll get back the following response:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": "Hello world",
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

### Return Raw Response

The `return_raw_response` configuration accepts a boolean.  If it is true, then clearskies will not wrap the response from the callable in the standard clearskies response format but will just return it as-is.  Take the following example:

{% highlight python %}
import clearskies

@clearskies.decorators.public()
@clearskies.decorators.return_raw_response()
def example_callable(test_binding):
    return f'Hello {test_binding}'

callable_demo = clearskies.contexts.wsgi(
    example_callable,
    bindings={
        'test_binding': 'world',
    }
)
def application(env, start_response):
    return callable_demo(env, start_response)
{% endhighlight %}

If you [run it locally](docs/running-examples.html#running-examples-designed-for-an-http-server) and call the server like so:

```
curl 'http://localhost:9090'
```

You will get the following response:

```
helloworld
```

### Schema

The `schema` option allows you to specify a schema that the incoming user data will be compared against.  This schema can take a few forms:

 1. A model class
 2. A model
 3. A list of column definitions (like you would define in a model class).

clearskies will validate any user input against the schema and, if it does not pass the requirements, will return an input error to the client without invoking your function.  It will also use the schema to populate the documentation for the endpoint in the autodocs.  See the following example of validation against a model class:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float
from clearskies.input_requirements import required
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name', input_requirements=[required()]),
            float('price'),
        ])

@clearskies.decorators.public()
@clearskies.decorators.schema(Product)
def example_callable(request_data):
    return request_data

callable_demo = clearskies.contexts.wsgi(example_callable)
def application(env, start_response):
    return callable_demo(env, start_response)
{% endhighlight %}

If you [run it locally](docs/running-examples.html#running-examples-designed-for-an-http-server) and call the server like so:

```
curl 'http://localhost:9090' -d '{"name": "toys", "price": 85.50}'
```

You will receive a response like so:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {
    "name": "toys",
    "price": 85.5
  },
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

And of course if you send invalid data:

```
curl 'http://localhost:9090' -d '{"price": "hey"}'
```

You would receive the expected input errors:

{% highlight json %}
{
  "status": "input_errors",
  "error": "",
  "data": [],
  "pagination": {},
  "input_errors": {
    "name": "'name' is required.",
    "price": "Invalid input: price must be an integer or float"
  }
}
{% endhighlight %}

Note that since price is **not** required, it will be absent from the `request_data` if not provided by the end user - clearskies will not automatically fill it with `None`.

Attaching a model class for the schema can be convenient if your endpoint is going to be interacting with a model class, but this won't help for one-off endpoints that aren't working with a model.  In this case you can just attach column definitions directly like so:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float
from clearskies.input_requirements import required

@clearskies.decorators.public()
@clearskies.decorators.schema([
    string('name', input_requirements=[required()]),
    float('price'),
])
def example_callable(request_data):
    return request_data

callable_demo = clearskies.contexts.wsgi(example_callable)
def application(env, start_response):
    return callable_demo(env, start_response)
{% endhighlight %}

### Writeable Columns

Writeable columns is mainly intended for working with a schema from a model.  It allows you to specify a sub-set of columns from the model that are writeable (which can help if the model has columns that are only intended for internal usage).  Consider the following example where a model with two columns is used as the schema but only one column is in the list of writeable columns:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float
from clearskies.input_requirements import required
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name', input_requirements=[required()]),
            float('price'),
        ])

@clearskies.decorators.schema(Product, writeable_columns=['price'])
@clearskies.decorators.public()
def example_callable(request_data):
    return request_data

callable_demo = clearskies.contexts.wsgi(example_callable)
def application(env, start_response):
    return callable_demo(env, start_response)

{% endhighlight %}

If you [run it locally](docs/running-examples.html#running-examples-designed-for-an-http-server) and call the server like so:

```
curl 'http://localhost:9090' -d '{"name": "toys", "price": 85.50}'
```

you will get an input error:

{% highlight json %}
{
  "status": "input_errors",
  "error": "",
  "data": [],
  "pagination": {},
  "input_errors": {
    "name": "Input column 'name' is not an allowed column"
  }
}
{% endhighlight %}

Since the `name` column is not in the list of writeable columns (even though it exists in the model) clearskies returns an input error if the client tries to set it.

**Note:** This has a subtle but important implication: it effectively disables the "required" setting of the `name` column.  Since the name is no longer exposed from this endpoint, and thus a client cannot set it, it clearly cannot be a required column here.

### Doc Model Name

`doc_model_name` allows you to set the name of the model that will be referenced when the response of the endpoint is documented by the autodoc system via OpenAPI3.0/swagger.  This only operates in conjunction with the `doc_response_data_schema` option, since otherwise clearskies doesn't know what the response looks like (and therefore can't document it).

### Doc Response Data Schema

`doc_response_data_schema` allows you to specify the schema of your response for the autodoc system.  Note that the Callable handler will not make an autodoc by itself, so you normally need the simple routing handler to demonstrate this behavior:

{% highlight python %}
import clearskies

def example_callable():
    return {
        "name": "hey",
        "price": 27.50,
    }

doc_demo = clearskies.contexts.wsgi(
    {
        'handler_class': clearskies.handlers.SimpleRouting,
        'handler_config': {
            'authentication': clearskies.authentication.public(),
            'schema_route': 'schema',
            'routes': [
                {
                    'path': 'example_callable',
                    'handler_class': clearskies.handlers.Callable,
                    'handler_config': {
                        'callable': example_callable,
                        'doc_model_name': 'product',
                        'doc_response_data_schema': [
                            clearskies.autodoc.schema.String('name'),
                            clearskies.autodoc.schema.Number('price'),
                        ]
                    },
                }
            ],
        },
    },
)
def application(env, start_response):
    return doc_demo(env, start_response)
{% endhighlight %}

If you [run it locally](docs/running-examples.html#running-examples-designed-for-an-http-server) you can see the resultant swagger doc like so:

```
curl 'http://localhost:9090/schema'
```
