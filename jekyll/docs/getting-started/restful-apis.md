---
layout: default
title: Restful APIs
parent: Getting Started
permalink: /docs/getting-started/restful-apis.html
nav_order: 4
---

# Restful APIs

clearskies has a variety of handlers that implement standard "kinds" of behaviors, but the most common is the RESTful API handler.  It manages standard CRUD (Create, Read, Update, Delete) operations for you, as well as search functionality.  The most basic configuration requires a model class as well as a list of columns to expose during read/write operations.  Here's a comprehensive example that you can run locally and which comes with a pre-populated, in-memory database for testing:

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
        'handler_class': clearskies.handlers.RestfulAPI,
        'handler_config': {
            'authentication': clearskies.authentication.public(),
            'model_class': Product,
            'search_handler': clearskies.handlers.SimpleSearch,
            'default_sort_column': 'name',
            'readable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale'],
            'writeable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale'],
            'searchable_columns': ['name', 'price', 'type', 'in_stock', 'on_sale'],
            'default_sort_column': 'name',
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

Drop that in a file and then [launch your WSGI server](/docs/running-examples.html#running-examples-designed-for-an-http-server).  You now have a fully functional REST API endpoint with full CRUD capabilities, pagination, and search.  Try out some commands against your application to get started:

```
curl 'http://localhost:9090'
curl 'http://localhost:9090/search?name=car'
curl 'http://localhost:9090/search?on_sale=1'
curl 'http://localhost:9090/1'
curl 'http://localhost:9090' -d '{"name":"new toy","price":25.00,"type":"kids","in_stock":1,"on_sale":0}'
curl -X PUT 'http://localhost:9090/1' -d '{"price":25.50,"on_sale":1}'
curl -X DELETE 'http://localhost:9090/2'
```
