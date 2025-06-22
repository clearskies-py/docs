---
layout: default
title: Get
parent: Handlers
permalink: /docs/handlers/get.html
nav_order: 8
---

# Get Handler

 1. [Overview](#overview)
 2. [Configuration](#configuration)
 3. [Using the Get Endpoint](#using-the-get-endpoint)

## Overview

The get handler takes care of fetching a record and return the information about it.  In general, it just requires a model class and a list of which columns should be returned in the output.  Note that routing is required to use the get handler, as it explicitly looks for the id of the record-to-get from the URL path.  Most often, this is handled automatically since it is typically exposed through the [RESTful API](/docs/handlers/restful-api.html).  However, the examples below show how to use it in isolation, and thus wrap everything in a simple router.

## Configuration

The get handler includes all the [standard configuration options](/docs/handlers/standard-configs.html).  In addition, it has the following options:

| Name | Required | Type          |
|------|----------|---------------|
| [model_class](#model-class) | Yes, unless `model` is provided | Model class |
| [model](#model) | Yes, unless `model_class` is provided | Model instance |
| [readable_columns](#readable_columns) | Yes | `List[str]`
| [where](#where) | No | `List[Union[str, Callable]]` |

### Model Class

The `model_class` configuration specifies the model class that the handler should work with (and therefore create records for).  You must specify either `model_class` or `model`: one must be provided, but never both.

See [the example below](#using-the-get-endpoint) for usage examples.

### Model

The `model` configuration specifies the model that the handler should work with (and therefore return results for).  You must specify either `model` or `model_class`: one must be provided, but never both.

See [the example below](#using-the-get-endpoint) for usage examples.

### Readable Columns

The `readable_columns` configuration specifies what columns from the model should be returned by the get handler.  This allows you to explicitly control the data returned.

See [the example below](#using-the-get-endpoint) for usage examples.

### Where

A list of additional filters to apply when searching for the record.  This allows you to limit what records a user is allowed to delete.  At its simplest, it can be a simple string containing any valid clearskies condition.  You can also pass in a callable, which will be given the models object and should return a new models object that has been filtered as needed.  This callable can request any declared clearskies dependencies as well as the following dependency names:

| Name | Value |
|------|-------|
| models | The base models object being used for the search |
| routing_data | Any routing data associated with the request |
| authorization_data | Any authorization data for the client, as determined by the authentication process |
| input_output | The full InputOutput object for the request. |

Note that, in practice, this feature overlaps substantially with authorization.  If your filtering is explicitly to enable authorization, then you should see [the authentication and authorization section](/docs/authn-authz/index.html) for the "proper" way to implement authorization.

Here's a partial example of using a callable to limit the delete call to records created in the past 7 days.  You can combine it with the full examples in the [using the delete endpoint](#using-the-get-endpoint) section below.

{% highlight python %}
def last_seven_days(models, utcnow):
    return models.where("created_at>" + (utcnow - datetime.timedelta(days=7)).isoformat())

delete_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.SimpleRouting,
    {
        "authentication": clearskies.authentication.public(),
        "routes": [
            {
                "path": "/{id}",
                "handler_class": clearskies.handlers.Get,
                "handler_config": {
                    "model_class": Product,
                    "where": [last_seven_days],
                },
            },
        ],
    },
    bindings={
        "memory_backend": clearskies.backends.example_backend([
            {"id": "1-2-3-4", "owner": "jane", "created_at": datetime.datetime.now().isoformat()},
            {"id": "2-3-4-5", "owner": "jane", "created_at": (datetime.datetime.now()-datetime.timedelta(days=5)).isoformat()},
            {"id": "4-5-6-7", "owner": "bob", "created_at": (datetime.datetime.now()-datetime.timedelta(days=14)).isoformat()},

        ])
    }
))
{% endhighlight %}

With the above example data, it is not possible to fetch record `4-5-6-7`.

## Using the Get Endpoint

Here's a basic example of using the delete endpoint:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, integer, created, updated, uuid
from clearskies.input_requirements import required
from collections import OrderedDict
import datetime

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            uuid('id'),
            string('owner'),
            created('created_at'),
        ])

get_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.SimpleRouting,
    {
        "authentication": clearskies.authentication.public(),
        "routes": [
            {
                "path": "/{id}",
                "handler_class": clearskies.handlers.Get,
                "handler_config": {
                    "model_class": Product,
                    "readable_columns": ['id', 'owner', 'created_at'],
                    "where": ['owner=bob'],
                },
            },
        ],
    },
    bindings={
        "memory_backend": clearskies.backends.example_backend([
            {"id": "1-2-3-4", "owner": "jane", "created_at": datetime.datetime.now().isoformat()},
            {"id": "2-3-4-5", "owner": "jane", "created_at": (datetime.datetime.now()-datetime.timedelta(days=5)).isoformat()},
            {"id": "4-5-6-7", "owner": "bob", "created_at": (datetime.datetime.now()-datetime.timedelta(days=14)).isoformat()},
        ])
    }
))
def application(env, start_response):
    return get_demo(env, start_response)

{% endhighlight %}

In this example, the example backend is being used to pre-populate an in-memory database.  The `where` condition of `owner=bob` means that only record `4-5-6-7` can be fetched.  You can see this by [launching the server](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then calling it like so:

```
curl 'http://localhost:9090/4-5-6-7'
```

Which will give a response like:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {
    "id": "4-5-6-7",
    "owner": "bob",
    "created_at": "2023-05-25T19:18:29.042221+00:00"
  },
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

If you tried to fetch a record which was "inaccessible" due to the `where` filter:

```
curl 'http://localhost:9090/1-2-3-4'
```

You would get this response:

{% highlight json %}
{
{
  "status": "client_error",
  "error": "Not Found",
  "data": [],
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

Note that the get handler doesn't do any routing of its own.  As a result, it would respond to any HTTP request method.  Typically this is wrapped up in one of the routing handlers (the [simple routing handler](/docs/handlers/simple-routing.html) or the [restful API handler](/docs/handlers/restful-api.html)) to ensure that it only responds to a GET request, for instance.

Finally, the above example assumes that the id field is named `id`.  Here's an example of working with a model that uses a different name for the id field:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, integer, created, updated, uuid
from clearskies.input_requirements import required
from collections import OrderedDict
import datetime

class Product(clearskies.Model):
    id_column_name = "record_identifier"

    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            uuid('record_identifier'),
            string('owner'),
            created('created_at'),
        ])

get_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.SimpleRouting,
    {
        "authentication": clearskies.authentication.public(),
        "routes": [
            {
                "path": "/{record_identifier}",
                "handler_class": clearskies.handlers.Get,
                "handler_config": {
                    "model_class": Product,
                    "where": ['owner=bob'],
                    "readable_columns": ['record_identifier', 'owner', 'created_at'],
                },
            },
        ],
    },
    bindings={
        "memory_backend": clearskies.backends.example_backend([
            {"record_identifier": "1-2-3-4", "owner": "jane", "created_at": datetime.datetime.now().isoformat()},
            {"record_identifier": "2-3-4-5", "owner": "jane", "created_at": (datetime.datetime.now()-datetime.timedelta(days=5)).isoformat()},
            {"record_identifier": "4-5-6-7", "owner": "bob", "created_at": (datetime.datetime.now()-datetime.timedelta(days=14)).isoformat()},
        ])
    }
))
def application(env, start_response):
    return get_demo(env, start_response)
{% endhighlight %}
