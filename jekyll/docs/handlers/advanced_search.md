---
layout: default
title: Advanced Search
parent: Handlers
permalink: /docs/handlers/advanced-search.html
nav_order: 2
---

# Advanced Search

 1. [Overview](#overview)
 2. [Configuration](#configuration)
 3. [Using the Search Endpoint](#using-the-search-endpoint)
 4. [Examples](#examples)

### Overview

The advanced search handler exposes an endpoint that allows the client to execute fairly arbitrary search criteria - searches on multiple columns, multiple searches on a single column, a variety of search operators, and sorting by more than one column.  Note, however, that the advanced search will ultimately be limited by your backend.  If your backend doesn't support the full search capabilities of the advanced search, then your clients may end up seeing 500s when making more complicated queries.  In general, you can expect this to work well with full-featured databases.  The memory backend is also designed to support the full search capabilities of the advanced search handler.

In addition, there is a backend (the advanced search backend) meant to work transparently with this handler.  The backend allows you to point a clearskies model at an API endpoint hosted with the advanced search backend.  Queries made with the standard query builder built into clearskies models will then be automatically translated into API calls to the advanced search backend.  The end result of this is that integrating a clearskies application with another application built in clearskies is very easy.  In essence, clearskies can automatically build SDKs for itself.

### Configuration

The advanced search backend uses the same configuration options as the [list handler](list.html#configuration).

### Using the Search Endpoint

The search endpoint for the advanced search backend looks for data in the JSON body or (in some cases) URL parameters.  Here are the allowed inputs:

| Name | Type | Location | Description |
|------|------|-------------|
| `limit` | `int` | Body or URL | The maximum number of entries to return |
| `start`* | `int` | Body or URL | Pagination data: the record to start on |
| `sort` | `List[Dict[str, str]]` | Body | Up to two sort directives of the form `{"column": "name", "direction": "asc|desc"}` |
| `where` | `List[Dict[str, str]]` | Body | Filter directirves of the form `{"column": "name": "operator": "=|<=|etc", "value": "search value"}` |

***Note:** Pagination (and thus the pagination data) is determined by the backend.  For memory and cursor backends, `start` is used as the pagaination parameter.  However, different backends use different pagination parmeters, so this can change.  Refer to the documentation for your specific backend to verify if something other than `start` is used.

### Examples

Here's a basic example of using the advanced search handler.  It uses the example backend to pre-populate data in the memory backend so that you can immediately test the endpoint:

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
        'handler_class': clearskies.handlers.AdvancedSearch,
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

[Run this example locally](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then you can try a simple curl request to reproduce the behavior of the List handler:

```
curl 'http://localhost:9090'
```

To see a more powerful seach, take this JSON document:

{% highlight json %}
{
  "sort": [
    {"column": "name", "direction": "desc"}
  ],
  "where": [
    {"column": "on_sale", "operator": "=", "value": 1},
    {"column": "price", "operator": "<", "value": 1000}
  ]
}
{% endhighlight %}

Save it to a file locally (for instance, `fancy_search.json`) and then in the same directory where you saved it, send it to your clearskies server:

```
curl 'http://localhost:9090' -d "@fancy_search.json"
```

and you will receive a response like this:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": [
    {
      "id": 3,
      "name": "chainsaw",
      "price": 250,
      "type": "tool",
      "in_stock": 10,
      "on_sale": 1
    }
  ],
  "pagination": {
    "number_results": 1,
    "limit": 100,
    "next_page": {}
  },
  "input_errors": {}
}
{% endhighlight %}
