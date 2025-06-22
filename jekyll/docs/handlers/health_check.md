---
layout: default
title: Health Check
parent: Handlers
permalink: /docs/handlers/health-check.html
nav_order: 9
---

# Health Check Handler

 1. [Overview](#overview)
 2. [Configuration](#configuration)

## Overview

The healthcheck handler is a simple way of building a health check.  You have two basic ways of building health checks.  One is to provide a list of "services" (which are just dependency names).  clearskies will build them and, assuming nothing crashes, return a success response.   You can also provide a callable to define your own health check functionality.

## Configuration

The health check handler only has two configuration options.  Neither is required.  If you don't declare any options, then the healthcheck will more or less just verify that your clearskies application doesn't have any obvious misconfigurations.  If you provide both, then the health check handler will check both and return success only if both succeed.

| Name | Required | Type          |
|------|----------|---------------|
| [services](#services) | No | `List[str]` |
| [callable](#callable) | No | `Callable` |

### Services

The servies configuration receives a list of dependencies and loads them.  If nothing crashes, then the health check will return a 200.  As an example of how you might want to use this, you can request the `cursor_backend`.  clearskies will attempt to connect to the database when it is requested, so if it cannot connect to the database then the health check will fail.  Here's an example which will (presumably) fail since the database is not configured:

{% highlight python %}
import clearskies

healthcheck_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.HealthCheck,
    {
        "services": ["cursor_backend"]
    },
))
def application(env, start_response):
    return healthcheck_demo(env, start_response)
{% endhighlight %}

You can [launch the server](/docs/running-examples.html#running-examples-designed-for-an-http-server) and then:

```
curl 'http://localhost:9090'
```

which will give you a `500` status code with a response of:

{% highlight json %}
{
  "status": "failure",
  "error": "",
  "data": [],
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

And here is an example which should always succeed, since the memory backend is always available:

{% highlight python %}
import clearskies

healthcheck_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.HealthCheck,
    {
        "services": ["memory_backend"]
    },
))
def application(env, start_response):
    return healthcheck_demo(env, start_response)
{% endhighlight %}

If you launch this version and call the server, you'll get a success response with a `200` status code:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": {},
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

### Callable

The `callable` configuration allows you to define your own health check.  Pass it a callable, and make sure to return True/False to denote if the service is healthy (of course, if your callable throws an exception, that will also cause a failed health check).  Your callable can request any configured dependency injection names to help with your health check.

{% highlight python %}
import clearskies

def is_healthy():
    return True

healthcheck_demo = clearskies.contexts.wsgi(clearskies.Application(
    clearskies.handlers.HealthCheck,
    {
        "callable": is_healthy
    },
))
def application(env, start_response):
    return healthcheck_demo(env, start_response)
{% endhighlight %}
