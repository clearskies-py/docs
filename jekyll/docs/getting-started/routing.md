---
layout: default
title: Routing
parent: Getting Started
permalink: /docs/getting-started/routing.html
nav_order: 2
---

# Routing

## Basics

In [our previous example](./callables.html) we executed a single function in a CLI context.   That's obviously pretty simple, but of course a real-world application will need some routing.  clearskies has a [simple routing handler](/docs/handlers/simple_routing.html) to provide detailed control over your routes as well as an autodoc system.  While this can be used directly like any handler, clearskies also comes with a decorator system to simplify usage:

{% highlight python %}
import clearskies

@clearskies.decorators.get('/user/{user_id}')
@clearskies.decorators.public()
def get_user(user_id):
    return user_id

@clearskies.decorators.post('/user/{user_id}')
@clearskies.decorators.public()
def update_user(request_data, user_id):
    print(f'Saving {user_id}')
    print(request_data)

cli = clearskies.contexts.cli([get_user, update_user])
cli()
{% endhighlight %}

[Setup this example to run from the CLI](/docs/running-examples.html#running-examples-designed-for-the-cli) and then execute it.  Note that, in a CLI context, clearskies translates URL-based paths (which are slash separated) into the space-based paths that a CLI program normally expects.  Therefore, this command:

```
./clearskies_example.py user 5 | jq
```

Will result in this response:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": "5",
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

In addition, clearskies expects a `request_method` parameter to reach POST endpoints in a CLI context, and the equivalent of JSON parameters are set via `--key=value` parameters.  Therefore, to call the POST endpoint from the CLI you would execute this command:

```
./clearskies_example.py user 5 --request_method=POST --name=bob | jq
```

with this result:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {
    "name": "bob",
    "id": "5"
  },
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

Of course, you may be building a web application, in which case the exact same code works fine with a different context:

{% highlight python %}
import clearskies

@clearskies.decorators.get('/user/{user_id}')
@clearskies.decorators.public()
def get_user(user_id):
    return user_id

@clearskies.decorators.post('/user/{user_id}')
@clearskies.decorators.public()
def update_user(request_data, user_id):
    return {
        **request_data,
        'id': user_id,
    }

in_wsgi = clearskies.contexts.wsgi([get_user, update_user])
def application(env, start_response):
    return in_wsgi(env, start_response)
{% endhighlight %}

[Launch your wsgi server](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then call your local application:

```
$ curl 'http://localhost:9090/user/5' | jq
{
  "status": "success",
  "error": "",
  "data": "5",
  "pagination": {},
  "input_errors": {}
}
```

Or:

```
$ curl 'http://localhost:9090/user/5' -d '{"name":"bob"}' | jq
{
  "status": "success",
  "error": "",
  "data": {
    "name": "bob",
    "id": "5"
  },
  "pagination": {},
  "input_errors": {}
}
```

**About CRUD endpoints**: Note that you shouldn't have to define standard CRUD (create, read, update, delete) endpoints because the [RESTful API handler](/docs/handlers/restful-api.html) can build those automatically for you.  Any business logic outside of simply reading/writing data to the backend goes in the model, and the RESTful API handler takes care of processing user input and calling save operations on the model.

## Defining Endpoints in Modules

You can also define your decorated functions in a module and then attach the module to the context.  Any additional submodules declared in your routing module will also be imported and exposed.  As an example, we can take our decorated functions from the last example and move them into their own file, which we will call `my_routes.py`:

{% highlight python %}
import clearskies

@clearskies.decorators.get('/user/{user_id}')
@clearskies.decorators.public()
def get_user(user_id):
    return user_id

@clearskies.decorators.post('/user/{user_id}')
@clearskies.decorators.public()
def update_user(request_data, user_id):
    return {
        **request_data,
        'id': user_id,
    }
{% endhighlight %}

We can then import those and expose them directly through our context:

{% highlight python %}
import clearskies
import my_routes

in_wsgi = clearskies.contexts.wsgi(my_routes)
def application(env, start_response):
    return in_wsgi(env, start_response)
{% endhighlight %}

This provies a simple and straight-forward way to make the same code base available in different ways.  You can, for example, expose a set of API endpoints to a Lambda function via one of the appropriate AWS-centric contexts, and then expose them through a WSGI server for local testing (or even through a CLI context if you don't want to worry about managing a local web server).

## Authorization

This is a good time to point out that authorization is an **explicit** requirement of endpoints in clearskies.  The only exception is for the CLI context, which automatically treats all endpoints as "public".  Therefore, if you create an endpoint but don't add an authorization method:


{% highlight python %}
import clearskies

@clearskies.decorators.get('/user/{user_id}')
def get_user(user_id):
    return user_id
{% endhighlight %}

You'll see this error message when you launch the service:

```
ValueError: I couldn't find any authentication rules while auto-importing your routes.  Make sure an add an authentication decorator to your routes, even if it's just @clearskies.decorators.public
```

## Additional Options

There is a decorator for [all the configuration options available to the callable handler](/docs/handlers/callable.html#configuration).  For the list and examples, [see the docs about decorators](/docs/routing-decorators/index.html).
