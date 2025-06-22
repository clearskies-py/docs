---
layout: default
title: Handlers
has_children: true
permalink: /docs/handlers/index.html
nav_order: 4
---

# Handlers

Handlers are a key feature of clearskies and also a differentiating factor from most other frameworks.  Typical frameworks are based around the concept of "when my endpoint is called execute this function that I will defined".  In contrast, clearskies comes with a variety of pre-defined "kinds" of functionality designed to fulfill common application needs.  That's where handlers come in.  The most basic handler is the `Callable` handler which will simply execute a function you defined.  Thus, you can still build your applications one function at a time, if you really want to.  However, if clearskies happens to have a handler that does what you are trying to do, then you can easily save hundreds of lines of code.  The most commonly used handlers might call a function, handle routing, implement a RESTful API, expose a healthcheck, generate your swagger documentation, etc...

To make use of handlers you specifcy the class of the one which you want clearskies to execute, as well as it's configuration - all handlers accept some configuration options to control their behavior.  Handlers can be packaged up in applications to create code which is ready to execute, as well as being attached directly to a context (as we have done thus far in our examples).

The simplest handler is the `Callable` handler, which simply executes a function.  We've already been using this in our examples thus far:

{% highlight python %}
#!/usr/bin/env python
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

my_cli_application = clearskies.contexts.cli(my_function)
my_cli_application()
{% endhighlight %}

When you attach a function to a context, you are implicitly using the `Callable` handler.  As such, the above code is short-hand for this:

{% highlight python %}
#!/usr/bin/env python
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

my_cli_application = clearskies.contexts.cli({
    'handler_class': clearskies.handlers.Callable,
    'handler_config': {
        'callable': my_function,
    }
})
my_cli_application()
{% endhighlight %}

Each handler class has its own configuration options that you can use to control its behavior.  For instance, with the callable handler, you can tell it not to wrap your response in the standard clearskies return structure:

{% highlight python %}
#!/usr/bin/env python
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

my_cli_application = clearskies.contexts.cli({
    'handler_class': clearskies.handlers.Callable,
    'handler_config': {
        'callable': my_function,
        'return_raw_response': True,
    }
})
my_cli_application()
{% endhighlight %}

If you execute this it will return something like:

```
2023-02-06T12:01:52.520465+00:00
```

Rather than the usual:

```
{"status": "success", "error": "", "data": "2023-02-06T12:01:52.520465+00:00", "pagination": {}, "input_errors": {}}
```
