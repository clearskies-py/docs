---
layout: default
title: Using Callables
parent: Getting Started
permalink: /docs/getting-started/callables.html
nav_order: 1
---

# Using Callables

As we'll see later on, clearskies uses handlers to determine the kind of behavior of your application.  However, the default handler in clearskies is a simple callable, which means that you provide a function and clearskies calls it, returning the response from your function on to whoever invoked your application.  Since clearskies is meant to run anywhere, you do have to create a context that corresponds to the way clearskies will be executed.  The simplest context is to execute it via the CLI, so the following example shows the most basic clearskies application:

{% highlight python %}
#!/usr/bin/env python
import clearskies

def my_function(utcnow):
    return utcnow.isoformat()

my_cli_application = clearskies.contexts.cli(my_function)
my_cli_application()
{% endhighlight %}

`utcnow` is one of many dependency injection names provided by clearskies by default.  It is populated with a datetime object set to the current time in the UTC time zone.  [Running the above program](/docs/running-examples#running-examples-designed-for-the-cli) should return something like this:

{% highlight json %}
{
  "status": "success",
  "error": "",
  "data": "2023-02-05T15:21:34.298956+00:00",
  "pagination": {},
  "input_errors": {}
}
{% endhighlight %}

Due to its web-focused nature, clearskies always returns JSON and has a standardized response format for all calls, which you can see above.
