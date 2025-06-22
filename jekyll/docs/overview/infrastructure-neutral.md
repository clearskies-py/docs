---
layout: default
title: Infrastructure Neutral
parent: Overview
permalink: docs/overview/infrastructure-neutral.html
nav_order: 2
---

# Infrastructure Neutral

To run code in clearskies you attach your application to a context: WSGI server, Lambda, Queue listener, CLI, test environment, etc... The same code can run in your production environment, on a dev machine, or in your test suite without making any changes.

Consider a simple hello world application that takes a name from a URL parameter and greets the caller:

{% highlight python %}
import clearskies

def hello_world(name):
    return f'Hello {name}!'
{% endhighlight %}

The following code would bootstrap it in the builtin test server:

{% highlight python %}
import clearskies

def hello_world(name):
    return f'Hello {name}!'

hello = clearskies.contexts.WsgiRef(
    clearskies.endpoints.Callable(
        hello_world,
        url="/:name"
    )
)
hello()
{% endhighlight %}

Changing the context and a minor tweak to how it is invoked allows you to create a WSGI application to launch with any WSGI server:

{% highlight python %}
import clearskies

def hello_world(name):
    return f'Hello {name}!'

hello = clearskies.contexts.Wsgi(
    clearskies.endpoints.Callable(
        hello_world,
        url="/:name"
    )
)
def wsgi_application(env, start_response):
    return hello(env, start_response)

api = clearskies_aws.contexts.lambda_api_gateway(hello_word)
def application(event, context):
    return api(event, context)
{% endhighlight %}

Or from the command line:

{% highlight python %}
cli = clearskies.contexts.cli(hello_word)
cli()
{% endhighlight %}
