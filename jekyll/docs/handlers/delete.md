---
layout: default
title: Delete
parent: Handlers
permalink: /docs/handlers/delete.html
nav_order: 7
---

# Delete Handler

 1. [Overview](#overview)
 2. [Configuration](#configuration)
 3. [Using the Delete Endpoint](#using-the-delete-endpoint)

## Overview

The delete handler takes care of delete requests.  In general, it just requires a model class.  Note that routing is required to use the delete handler, as it explicitly looks for the id of the record-to-delete from the URL path.  Most often, this is handled automatically since it is typically exposed through the [RESTful API](/docs/handlers/restful-api.html).  However, the examples below show how to use it in isolation, and thus wrap everything in a simple router.

## Configuration

The delete handler includes all the [standard configuration options](/docs/handlers/standard-configs.html).  In addition, it has the following options:

| Name | Required | Type          |
|------|----------|---------------|
| [model_class](#model-class) | Yes, unless `model` is provided | Model class |
| [model](#model) | Yes, unless `model_class` is provided | Model instance |
| [where](#where) | No | Additional filters to apply when searching for the requested model. |

### Model Class

The `model_class` configuration specifies the model class that the handler should delete records from.  You must specify either `model_class` or `model`: one must be provided, but never both.

See [the example below](#using-the-delete-endpoint) for usage examples.

### Model

The `model` configuration specifies the model that the handler should work with (and therefore return results for).  You must specify either `model` or `model_class`: one must be provided, but never both.

See [the example below](#using-the-delete-endpoint) for usage examples.

### Where

A list of additional filters to apply when searching for the record.  This allows you to limit what records a user is allowed to delete.  At its simplest, it can be a simple string containing any valid clearskies condition.  You can also pass in a callable, which will be given the models object and should return a new models object that has been filtered as needed.  This callable can request any declared clearskies dependencies as well as the following dependency names:

| Name | Value |
|------|-------|
| models | The base models object being used for the search |
| routing_data | Any routing data associated with the request |
| authorization_data | Any authorization data for the client, as determined by the authentication process |
| input_output | The full InputOutput object for the request. |

Note that, in practice, this feature overlaps substantially with authorization.  If your filtering is explicitly to enable authorization, then you should see [the authentication and authorization section](/docs/authn-authz/index.html) for the "proper" way to implement authorization.

Here's a partial example of using a callable to limit the delete call to records created in the past 7 days.  You can combine it with the full examples in the [using the delete endpoint](#using-the-delete-endpoint) section below.

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
                "handler_class": clearskies.handlers.Delete,
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

With the above example data, it is not possible to delete record `4-5-6-7`.

## Using the Delete Endpoint

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

delete_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.SimpleRouting,
    {
        "authentication": clearskies.authentication.public(),
        "routes": [
            {
                "path": "/{id}",
                "handler_class": clearskies.handlers.Delete,
                "handler_config": {
                    "model_class": Product,
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
    return delete_demo(env, start_response)
{% endhighlight %}

In this example, the example backend is being used to pre-populate an in-memory database.  The `where` condition of `owner=bob` means that only record `4-5-6-7` can be deleted.  You can see this by [launching the server](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then calling it like so:

```
curl 'http://localhost:9090/4-5-6-7'
```

Which will give a response like:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {},
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

If you tried to delete a record which was "inaccessible" due to the `where` filter:

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

Note that the delete handler doesn't do any routing of its own.  As a result, it would respond to any HTTP request method.  Typically this is wrapped up in one of the routing handlers (the [simple routing handler](/docs/handlers/simple-routing.html) or the [restful API handler](/docs/handlers/restful-api.html)) to ensure that it only responds to a DELETE request, for instance.

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

delete_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.SimpleRouting,
    {
        "authentication": clearskies.authentication.public(),
        "routes": [
            {
                "path": "/{record_identifier}",
                "handler_class": clearskies.handlers.Delete,
                "handler_config": {
                    "model_class": Product,
                    "where": ['owner=bob'],
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
    return delete_demo(env, start_response)
{% endhighlight %}
