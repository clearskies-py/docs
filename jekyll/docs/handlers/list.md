---
layout: default
title: List
parent: Handlers
permalink: /docs/handlers/list.html
nav_order: 10
---

# List

 1. [Overview](#overview)
 2. [Configuration](#configuration)
 3. [Examples](#examples)

## Overview

The List handler returns lists of records to the client.  It's also used as a base class for the various kinds of search handlers.  It's children all share the same basic configuration options, which are described below

## Configuration

The list backend has the following configuration options:

| Name | Required | Type          |
|------|----------|---------------|
| [model_class](#model-class) | Yes, unless `model` is provided | Model class |
| [model](#model) | Yes, unless `model_class` is provided | Model instance |
| [default_sort_column](#default-sort-column) | Yes | `str` |
| [readable_columns](#readable-columns) | Yes | `List[str]` |
| [searchable_columns](#searchable-columns) | Yes (if supported) | `List[str]` |
| [sortable_columns](#sortable-columns) | No | `List[str]` |
| [default_sort_direction](#default-sort-column) | No | `str` |
| [default_limit](#default-limit) | No | `int` |
| [max_limit](#max-limit) | No | `int` |
| [where](#where) | No | `List[Union[Callable, str]]` |
| [join](#join) | No | `List[str]` |
| [group_by](#group-by) | No | `List[str]` |

You can also use [all of the standard configurations provided by the handler base class](standard-configs).

### Model Class

The `model_class` configuration specifies the model class that the handler should work with (and therefore return results for).  You must specify either `model_class` or `model`: one must be provided, but never both.

### Model

The `model` configuration specifies the model that the handler should work with (and therefore return results for).  You must specify either `model` or `model_class`: one must be provided, but never both.

### Default Sort Column

This is the name of the column that the results should be sorted by, by default.  Of course, the column name must exist in the model schema and have a type that supports sorting (which most do)

### Readable Columns

A list of column names from the model which should be included in the data returned to the client.  Of course, each column must exist in the model schema.

### Searchable Columns

A list of column names from the model which the client is allowed to search by.  Of course, each column must exist in the model schema and have a type that supports searching.  Note that the base `List` handler itself does **not** support searching and so this is not required or applicable when using the `List` handler.  However, all the child classes of the `List` handler support searching and require this configuration setting.

### Sortable Columns

A list of column names from the model which the client can have the results sorted by.  Of course, each column must exist in the model schema and have a type that supports sorting.

### Default Sort Direction

The default direction that the results should be sorted by.  By default, the sort direction is `asc`.  Allowed values are `asc` or `desc`.

### Default Limit

The default number of records to return.  This is `100` by default.

### Max Limit

The maximum record limit that a user can request.  This is `200` by default but you can turn this as high as you want, but of course response times will increase when returning large number of records.  It is not possible to completely disable the limit.

### Where

A list of query conditions that should always be applied to the results.  The conditions can take one of two forms:

 1. A literal query condition (e.g. 'status=open', 'price>=100')
 2. A function which must accept (and return) a model object as well as other dependencies

Note that both options can be used together.  For the first option, the query string will be automatically passed along to the models object when fetching records.  Here's a partial example:

```
cheap_sales = clearskies.Application(
    clearskies.handlers.List,
    {
        'model_class': models.Product,
        'default_sot_column': 'name',
        'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale', 'sale_end_date'],
        'where': [
            'on_sale=1',
            'price<15',
        ]
    }
)
```

And here's an example of using the second option (as well as combining it with the first):

```
def sale_ending_soon(models, utcnow, input_output, routing_data):
    return models.where('sale_end_date<' + (utcnow+datetime.timedelta(days=1)).isoformat())

cheap_sales_ending_soon = clearskies.Application(
    clearskies.handlers.List,
    {
        'model_class': models.Product,
        'default_sot_column': 'name',
        'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale', 'sale_end_date'],
        'where': [
            'price<15',
            sale_ending_soon,
        ]
    }
)
```

### Join

The `join` configuration allows you to provide a list of join instructions which are set on the models object (via `models.join()`) before fetching records.

```
tag_filter = clearskies.Application(
    clearskies.handlers.List,
    {
        'model_class': models.Product,
        'default_sot_column': 'name',
        'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale', 'sale_end_date'],
        'join': [
            "JOIN tags ON tags.product_id=products.id AND tags.name='new'",
        ]
    }
)
```

### Group By

The `group_by` configuration allows you to provide a column to group the underlying query on, which is passed in via the `models.group_by()` method before fetching reocrds.

```
tag_filter = clearskies.Application(
    clearskies.handlers.List,
    {
        'model_class': models.Product,
        'default_sot_column': 'name',
        'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale', 'sale_end_date'],
        'group_by': 'type',
    }
)
```

## Examples

Here's a basic example of using the list handler.  It uses the example backend to pre-populate data in the memory backend so that you can immediately test the endpoint:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, integer, datetime
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, example_products_backend, columns):
        super().__init__(example_products_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name'),
            float('cost'),
            float('price'),
            string('type'),
            integer('in_stock'),
            integer('on_sale'),
        ])

products_api = clearskies.contexts.wsgi(
    {
        'handler_class': clearskies.handlers.List,
        'handler_config': {
            'authentication': clearskies.authentication.public(),
            'model_class': Product,
            'default_sort_column': 'name',
            'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale'],
        },
    },
    bindings={
        'example_products_backend': clearskies.BindingConfig(
            clearskies.backends.ExampleBackend,
            data=[
                {'id': 1, 'name': 'toy', 'price': 52.50, 'type': 'kids', 'in_stock': 150, 'on_sale': 0},
                {'id': 2, 'name': 'car', 'price': 32000, 'type': 'vehicle', 'in_stock': 1, 'on_sale': 1},
                {'id': 3, 'name': 'chainsaw', 'price': 250, 'type': 'tool', 'in_stock': 10, 'on_sale': 1},
            ]
        )
    }
)
def application(env, start_response):
    return products_api(env, start_response)
{% endhighlight %}

[Run this example locally](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then you can try a simple curl request:

```
curl 'http://localhost:9090'
```

and you will see results like so:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": [
    {
      "id": 2,
      "name": "car",
      "price": 32000,
      "type": "vehicle",
      "in_stock": 1,
      "on_sale": 1
    },
    {
      "id": 3,
      "name": "chainsaw",
      "price": 250,
      "type": "tool",
      "in_stock": 10,
      "on_sale": 1
    },
    {
      "id": 1,
      "name": "toy",
      "price": 52.5,
      "type": "kids",
      "in_stock": 150,
      "on_sale": 0
    }
  ],
  "pagination": {
    "number_results": 3,
    "limit": 100,
    "next_page": {}
  },
  "input_errors": {}
}
{% endhighlight %}

When calling the base list endpoint you can set the following settings in a URL parameter:

| Name | Description |
| `sort` | The name of the column to sort by |
| `direction` | The direction to sort (`asc` or `desc`) |
| `start`* | Pagination control |
| `limit` | The maximum number of records to return |

To see how these work, try out the following curl commands against your local server:

```
# change sort column/direction
curl 'http://localhost:9090?sort=name&direction=desc'

# change limit and note the `next_page` parameter in the `pagination` key of the response
curl 'http://localhost:9090?start=1&limit=1'

# invalid sort direction results in 4xx error
curl 'http://localhost:9090?sort=not-a-column&direction=desc'
```

***Note**: The pagination parameters are backend specific.  The memory and cursor backends use `start`, but different backends may expect different column names and also return different data in the `pagination` key of the response.  The pagination columns are documented on a per-backend basis.  As a result, the exact behavior exposed by the List handler may vary with your choice of backend.  Note that this fact is automatically reflected in the auto documentation generated by clearskies.
