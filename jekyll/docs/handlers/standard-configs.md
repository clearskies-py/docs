---
layout: default
title: Standard Configs
parent: Handlers
permalink: /docs/handlers/standard-configs.html
nav_order: 1
---

# Standard Configs

This is the list of standard configuration values for handlers in clearskies.  Examples below.

| Name | Type          | Description |
|------|---------------|-------------|
| [response_headers](#response-headers) | Dict | Additional headers to include in the response |
| [authentication](#authentication) | clearskies.authentication | Authentication object to authenticate the request |
| [authorization](#authorization) | Class or callable | Authorization rules for the endpoint |
| [output_map](#output-map) | Callable | Function to modify the final response to the client |
| [column_overrides](#column-overrides) | Dict | New column definitions |
| [doc_description](#doc-description) | str | A description to include in the various auto-documentation outputs |
| [internal_casing](#internalexternal-casing) | str | Controls the casing of auto-generated responses |
| [external_casing](#internalexternal-casing) | str | Controls the casing of auto-generated responses |
| [security_headers](#security-headers) | List | Specify the configuration of security headers to include in the response |

### Response Headers

The `response_headers` configuration specifies additional headers to send along with the request.  This is ignored if the context is not HTTP-compatible (e.g. the cli context).  `response_headers` should be a dictionary with key/value pairs.  In the below example we add an additional response header of `Content-Language: en`:

{% highlight python %}
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

application_with_headers = clearskies.contexts.wsgi({
    'handler_class': clearskies.handlers.Callable,
    'handler_config': {
        'authentication': clearskies.authentication.public(),
        'callable': my_function,
        'response_headers': {
            'content-language': 'en',
        }
    }
})

def application(env, start_response):
    return application_with_headers(env, start_response)
{% endhighlight %}

[Run it locally](/docs/running-examples#running-examples-designed-for-an-http-server) and then call it like so:

```
curl -i 'http://localhost:9090'
```

You'll get back a response with the expected header:

```
HTTP/1.1 200 Ok
CONTENT-TYPE: application/json
CONTENT-LANGUAGE: en

{"status": "success", "error": "", "data": "2023-02-06T16:15:08.529106+00:00", "pagination": {}, "input_errors": {}}
```

### Authentication

Clearskies explicitly requires an authentication object for all HTTP-compatible contexts.  When operating in the CLI context, the authentication is automatically set to public.  For more details and examples, see the [authentication/authorization](/docs/authn-authz) section of the docs.  Here's a quick example on how to specify a public endpoint:

```
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

application_with_headers = clearskies.contexts.wsgi({
    'handler_class': clearskies.handlers.Callable,
    'handler_config': {
        'authentication': clearskies.authentication.public(),
        'callable': my_function,
    }
})

def application(env, start_response):
    return application_with_headers(env, start_response)
```

### Authorization

There are a variety of options for enfocring authorization on your endpoints.  This is a key aspect of clearskies, so [it has its own section in the documentation](/docs/authn-authz).

### Output Map

Sometimes the output created by clearskies handlers just isn't quite what you need.  The output map fixes that.  You provide a function which will be called for each record in the response, and the function returns the final data that should be passed along to the client.  Here's an example API that returns a modified product record via the `output_map` configuration setting in the RESTful API handler:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, created, updated
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name'),
            string('description'),
            float('price'),
            created('created_at'),
            updated('updated_at'),
        ])

def output_product(product):
    return {
        'name': product.name.upper(),
        'price': product.price,
        'discounted_price': product.price*0.5,
    }

products_api = clearskies.contexts.wsgi({
    'handler_class': clearskies.handlers.RestfulAPI,
    'handler_config': {
        'output_map': output_product,
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

[Run it locally](/docs/running-examples#running-examples-designed-for-an-http-server) and then create a record, grabbing out the data returned for the new record:

```
curl 'http://localhost:9090' -d '{"name": "test product", "price": 15.50}' | jq '.data'
```

and you'll see something like this:

{% highlight json %}
{
  "name": "TEST PRODUCT",
  "price": 15.5,
  "discounted_price": 7.75
}
{% endhighlight %}

### Column Overrides

Column overrides allow you to change the definition of the columns for the underlying model used by the handler.  A common use case for this is if separate endoints have different input requirements.  Note though that it is not possible to remove an input requirement with overrides - only to add or change its configuration.  Finally, while changing input requirements is the primary use-case, it is possible to use this feature to change any aspect of a column - including its type.

In the following example, the `name` column is made required with `column_overrides`, and the maximum length of the `description` column is decreased from 255 characters to 10.:

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, created, updated
from clearskies.input_requirements import required, max_length
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name'),
            string('description', input_requirements=[max_length(255), required()]),
            float('price'),
            created('created_at'),
            updated('updated_at'),
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
        'column_overrides': {
            'name': {'input_requirements': [required()]},
            'description': {'input_requirements': [max_length(10)]},
        },
    }
})
def application(env, start_response):
    return products_api(env, start_response)
{% endhighlight %}

[Run it locally](/docs/running-examples#running-examples-designed-for-an-http-server) and then try to create a record like so:

```
curl 'http://localhost:9090' -d '{"description": "this is too longasdfasdfasdf"}' | jq
```

and you'll see something like this:

{% highlight json %}
{
  "status": "input_errors",
  "error": "",
  "data": [],
  "pagination": {},
  "input_errors": {
    "name": "'name' is required.",
    "description": "'description' must be at most 10 characters long."
  }
}
{% endhighlight %}

### Doc Description

Sets the description of the endpoint in the various auto-documentation systems that clearskies can output.

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, created, updated
from clearskies.input_requirements import required, maximum_length
from collections import OrderedDict

def do_thing():
    return 'The thing is done!'

api = clearskies.contexts.wsgi({
    'handler_class': clearskies.handlers.SimpleRouting,
    'handler_config': {
        'schema_route': 'schema',
        'schema_authentication': clearskies.authentication.public(),
        'authentication': clearskies.authentication.public(),
        'routes': [
            {
                'path': 'do-it',
                'handler_class': clearskies.handlers.Callable,
                'handler_config': {
                    'callable': do_thing,
                    'doc_description': 'Call this endpoint to get things done',
                }
            }
        ]
    }
})
def application(env, start_response):
    return api(env, start_response)
{% endhighlight %}

[Run it locally](/docs/running-examples#running-examples-designed-for-an-http-server) and then view the schema:

```
curl 'http://localhost:9090/schema'
```

### Internal/External Casing

The internal and external casing configurations work together to modify the casing of parameter names in requests.  This can be used if the naming conventions used in the backend need to be different than what the frontend wants.  Both must be specified together.  Allowed values for casings are:

 1. `snake_case`
 2. `camelCase`
 3. `TitleCase`

`internal_casing` should correspond to the casing style used in your models, while `external_casing` corresponds to the one desired for your endpoints.

{% highlight python %}
import clearskies
from clearskies.column_types import string, float, created, updated
from collections import OrderedDict

class Product(clearskies.Model):
    def __init__(self, memory_backend, columns):
        super().__init__(memory_backend, columns)

    def columns_configuration(self):
        return OrderedDict([
            string('name'),
            string('description'),
            float('price'),
            created('created_at'),
            updated('updated_at'),
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
        'internal_casing': 'snake_case',
        'external_casing': 'TitleCase',
    }
})
def application(env, start_response):
    return products_api(env, start_response)
{% endhighlight %}

[Run it locally](/docs/running-examples#running-examples-designed-for-an-http-server) and then create a record:

```
curl 'http://localhost:9090' -d '{"name":"Test Product","description":"Does Cool Things"}' | jq
```

and you'll see a response in TitleCase:

{% highlight json %}
{
  "Status": "Success",
  "Error": "",
  "Data": {
    "Id": "b8a96914-c4e5-4965-b52b-0bf574e3641f",
    "Name": "Test Product",
    "Description": "Does Cool Things",
    "Price": null,
    "CreatedAt": "2023-02-10T19:41:44+00:00",
    "UpdatedAt": "2023-02-10T19:41:44+00:00"
  },
  "Pagination": {},
  "InputErrors": {}
}
{% endhighlight %}

### Security Headers

clearskies comes with ready-to-use configurations for security headers.  They can be dropped into an endpoint via the `security_headers` configuration.  Since there are a variety of possible security headers, the details are [documented elsewhere](/docs/security-headers/index.html).
