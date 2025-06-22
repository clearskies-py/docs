---
layout: default
title: Create
parent: Handlers
permalink: /docs/handlers/create.html
nav_order: 4
---

# Create Handler

 1. [Overview](#overview)
 2. [Configuration](#configuration)
 3. [Using the Create Endpoint](#using-the-create-endpoint)

## Overview

The create handler takes care of create requests to generate records in your backend.  In general, it requires a model class and a list of columns that the client is allowed to set.  It will perform strict input validation against the schema of your model and return detailed error messages to the client in the case of input errors.

It's worth taking a moment to highlight the "clearskies" way.  In most frameworks you would use write the actual code for your create endpoint, and thus you would have an obvious way to inject any custom logic you need during the create process.  Not so with clearskies.  After input validation, the create handler will invoke the `save` function on your model **without** any room for you to customize the save behavior.  Therefore, any additional behavior you need should go in your model, or the columns of the model (all of which have extensive lifecycle hooks and triggers to make it easy to add in your business logic).  This encourages reusability and substantially decreases the time it takes to generate and manages APIs.

## Configuration

The create handler includes all the [standard configuration options](/docs/handlers/standard-configs.html).  In addition, it has the following options:

| Name | Required | Type          |
|------|----------|---------------|
| [model_class](#model-class) | Yes, unless `model` is provided | Model class |
| [model](#model) | Yes, unless `model_class` is provided | Model instance |
| [readable_columns](#readable-columns) | Yes | `List[str]` |
| [writeable_columns](#writeable-columns) | Yes | `List[str]` |
| [input_error_callable](#input-error-callable) | No | `Callable` |
| [column_overrides](#column-overrides) | No | `Dict[str, Any]` |

### Model Class

The `model_class` configuration specifies the model class that the handler should work with (and therefore create records for).  You must specify either `model_class` or `model`: one must be provided, but never both.

See [the example below](#using-the-create-endpoint) for usage examples.

### Model

The `model` configuration specifies the model that the handler should work with (and therefore return results for).  You must specify either `model` or `model_class`: one must be provided, but never both.

See [the example below](#using-the-create-endpoint) for usage examples.

### Readable Columns

A list of column names from the model which should be included in the data returned to the client.  Of course, each column must exist in the model schema.

See [the example below](#using-the-create-endpoint) for usage examples.

### Writeable Columns

A list of column names from the model which the client is allowed to set when creating a model.  Of course, each column must exist in the model schema.

**IMPORTANT**: Note that a required column that is not a writeable column will obviously not be a required input (since the client is not allowed to specify it).

See [the example below](#using-the-create-endpoint) for usage examples.

### Input Error Callable

A callable that will be passed the user input and can perform additional input validation checks not specified in the model/columns.  The input error callable should return a dictionary with the input error: the key should be the column name and the value should be a human readable error message.  In the event that there are no errors found, it should return an empty dictionary.

The input error callable can request any dependency provided by the clearskies application, and can also request any of the following parameters:


| Name                 | Value |
|----------------------|----------|
| `input_data`         | A dictionary with the raw input from the client |
| `input_output`       | The full InputOutput instance for the call |
| `routing_data`       | A dictionary with the routing data for the call (e.g. any data from the URL) |
| `authorization_data` | A dictionary with any authorization data from the authentication process |

Here's a partial example of enabling a custom input check.  See [using the create endpoint](#using-the-create-endpoint) for a complete example that you can drop this into.

{% highlight python %}
def my_input_errors(request_data):
    errors = {}
    if request_data.get('price') > 10000:
        errors['price'] = "Too rich for my blood."
    return errors

create_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.Create,
    {
        "authentication": clearskies.authentication.public(),
        "model_class": Product,
        "writeable_columns": ["name", "description", "price", "in_stock"],
        "readable_columns": ["id", "name", "description", "price", "in_stock", "created_at", "updated_at"],
        "input_error_callable": my_input_errors,
    }
))
{% endhighlight %}

### Column Overrides

A dictionary of overrides for columns in your model.  This allows you to change aspects of the columns for this specific endpoint.  Here's a partial example that turns the price column into an integer and makes it required.  See [using the create endpoint](#using-the-create-endpoint) for a complete example that you can drop this into.

{% highlight python %}
create_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.Create,
    {
        "authentication": clearskies.authentication.public(),
        "model_class": Product,
        "writeable_columns": ["name", "description", "price", "in_stock"],
        "readable_columns": ["id", "name", "description", "price", "in_stock", "created_at", "updated_at"],
        "column_overrides": OrderedDict([
            integer('price', input_requirements=[required()]),
        ]),
    }
))
{% endhighlight %}

## Using the Create Endpoint

Here's a basic example of using the create endpoint:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, integer, created, updated, uuid
from clearskies.input_requirements import required
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            uuid('id'),
            string('name', input_requirements=[required()]),
            string('description'),
            float('price'),
            integer('in_stock'),
            created('created_at'),
            updated('updated_at'),
        ])

create_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.Create,
    {
        "authentication": clearskies.authentication.public(),
        "model_class": Product,
        "writeable_columns": ["name", "description", "price", "in_stock"],
        "readable_columns": ["id", "name", "description", "price", "in_stock", "created_at", "updated_at"],
    }
))
def application(env, start_response):
    return create_demo(env, start_response)
{% endhighlight %}

You can then [launch the server](/docs/running-examples.html#running-examples-designed-for-an-http-server) and call it like so:

```
curl 'http://localhost:9090' -d '{"name": "My cool product", "description": "", "price": 25.50, "in_stock": 234}'
```

Which will give a response like:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {
    "id": "1528c499-a841-43e0-8850-8c1d2799db1f",
    "name": "My cool product",
    "description": "",
    "price": 25.5,
    "in_stock": 234,
    "created_at": "2023-06-08T07:44:38+00:00",
    "updated_at": "2023-06-08T07:44:38+00:00"
  },
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

To see the input validation you could try a request like this:

```
curl 'http://localhost:9090' -d '{"description": 1234, "price": "hey", "in_stock": 34.8}'
```

{% highlight json %}
{
  "status": "input_errors",
  "error": "",
  "data": [],
  "pagination": {},
  "input_errors": {
    "name": "'name' is required.",
    "description": "value should be a string",
    "price": "Invalid input: price must be an integer or float",
    "in_stock": "in_stock must be an integer"
  }
}
{% endhighlight %}

Note that the create handler doesn't have any built in routing.  As a result, it would respond to any HTTP request method.  Typically this is wrapped up in one of the routing handlers (the [simple routing handler](/docs/handlers/simple-routing.html) or the [restful API handler](/docs/handlers/restful-api.html)).
