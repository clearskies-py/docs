---
layout: default
title: Declarative APIs
parent: Overview
permalink: /docs/overview/declarative-apis.html
nav_order: 4
---

# Declarative APIs

Creating APIs via [declarative programming principles](https://en.wikipedia.org/wiki/Declarative_programming) means that you tell clearskies what you want done instead of how to do it. Create your models and tell clearskies which columns to expose. From there, clearskies will generate a fully functional API endpoint! It will even automatically generate your OAI3.0/Swagger docs. It can even host them from your application so that your docs automatically update themselves as you push out changes.  Consider the following example which builds a simple products API:

{% highlight python %}
import clearskies
from collections import OrderedDict


class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            clearskies.column_types.string(
                'name',
                input_requirements=[clearskies.input_requirements.required()]
            ),
            clearskies.column_types.string(
                'description',
                input_requirements=[clearskies.input_requirements.required()]
            ),
            clearskies.column_types.float('price'),
            clearskies.column_types.created('created_at'),
            clearskies.column_types.updated('updated_at'),
        ])

products_api = clearskies.contexts.wsgi({
    'handler_class': clearskies.handlers.RestfulAPI,
    'handler_config': {
        'authentication': clearskies.authentication.public(),
        'model_class': Product,
        'readable_columns': ['name', 'description', 'price', 'created_at', 'updated_at'],
        'writeable_columns': ['name', 'description', 'price'],
        'searchable_columns': ['name', 'description', 'price'],
        'default_sort_column': 'name',
    }
})
def application(env, start_response):
    return products_api(env, start_response)
{% endhighlight %}

It uses the built-in memory backend, so you can save the above to a file and launch it directly without having to setup a database.  You just need a WSGI server (if you don't have one, you can probably get [this one](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html) by running `pip install uwsgi` or `pip3 install uwsgi`).  Then you can launch your API from the command line:

```
uwsgi --http :9090 --wsgi-file my_products_api.py
```

and finally you can execute curl commands against your new API:

```
curl 'http://localhost:9090' \
    -d '{"name":"My First API","description":"A great start","price":125.50}'
```

Which responds with something like:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {
    "id": "54737cea-9529-48b6-aceb-48ce72347cbf",
    "name": "my first API",
    "description": "A great start",
    "price": 125.50,
    "created": "2023-02-04T14:47:11+00:00",
    "updated": "2023-02-04T14:47:11+00:00"
  },
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

It comes with strict error checking.  With this curl command we'll leave out the name (which we declared as required in our model) and also pass in a string for the price:

```
curl 'http://localhost:9090' \
    -d '{"name":"","description":"A great start","price":"my dear aunt sally"}'
```

which returns:

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

Finally, the API endpoints come with pagination as well as a robust search system.  If you don't like the exact specifics of how clearskies builds the API, that's okay though, because everything in clearskies can be modified.
