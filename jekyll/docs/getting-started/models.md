---
layout: default
title: Models
parent: Getting Started
permalink: /docs/getting-started/models.html
nav_order: 3
---

# Using Models

Models are an important part of clearskies as they are used for interacting with the backend - databases, in-memory stores, APIs, and more.  By acting like an integration layer between your code and your backend, it brings consistency to your applications which makes them easier to understand.  In addition, they define a schema which provides input validation while using clearskies.  Every model class needs a constructor which accepts (and passes along to the parent constructor) two arguments: the backend and the `columns` object (which is used to manage the schema).  Here is an example of a `Product` model that uses the in-memory backend:

{% highlight python %}
#!/usr/bin/env python
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
{% endhighlight %}

The `__init__` method accepts a `memory_backend` object and the `columns` object.  These are two pre-defined dependency injection values in clearskies.  The `memory_backend` object is what causes this model class to use the in-memory data store available in clearskies.  As a different example, had the init method been defined like so:

```
    def __init__(self, cursor_backend, columns):
        super().__init__(cursor_backend, columns)
```

Then it would try to connect to an SQL database and use that for a datastore.  There are [a few kinds of backends available in clearskies](/docs/backends/index.html), and of course you can easily define and include your own, dropping them into a model in the same basic way.

Next, the model declares a schema with 5 columns with various column types: a `name` column (which is a string), a `description` column (also a string), a `price` column (a float), a `created_at` column (of the `created` type), and an `updated_at` column (of the `updated` time).  The last two columns are special datetime columns.  A column with the `created` column type will automatically record the time when a model is created.  Similarly, a column with the `updated` column type automatically records when the model is updated.

To use our model, we need to inform our dependency injection container about it and then our function can request it as a parameter.  The dependency injection system for clearskies looks at parameter names to decide what to inject, rather than variable types.  In accordance with PEP8, dependency injection names use snake case by default (since PEP8 dictates that varible names should be in snake case).  Therefore, when you tell clearskies to provision a class for dependency injection, it automatically converts the class name into snake case to generate the dependency injection name.  Finally, for the special case of models, clearskies also makes it available under the pluralized version of the class name.  This allows the "grammar" of your application to be more readable.  Here's some examples of declaring our model, creating a function that uses it to create/modify/sort through records, and then executing it in the CLI context:

{% highlight python %}
#!/usr/bin/env python3
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

def manage_products(products):
    # let's create some products
    dog_food = products.create({
        'name': 'Dog Food',
        'description': 'High quality dog food',
        'price': 56.75,
    })
    cat_food = products.create({
        'name': 'Cat Food',
        'description': 'High quality cat food',
        'price': 45.22,
    })
    products.create({
        'name': 'Dog Toy',
        'description': 'Squeeky McSqueekerson',
        'price': 12.50,
    })

    # let's double the price of our dog food
    dog_food.save({'price': dog_food.price*2})
    # and check the price
    print(f'The new price of dog food: {dog_food.price}')

    # let's find our dog toy again and update its description
    dog_toy = products.find('name=Dog Toy')
    dog_toy.save({'description': 'Now extra squeeky!'})

    # and finally let's print out a summary of what we have:
    for product in products.where(:
        print(f'{product.name} sells for {product.price} and it is {product.description}')

if __name__ == '__main__':
    cli = clearskies.contexts.cli(
        manage_products,
        binding_classes=[Product],
    )
    cli()
{% endhighlight %}

[Running this](/docs/running-examples#running-examples-designed-for-the-cli`) will print out:

```
The new price of dog food: 113.5
Dog Food sells for 113.5 and it is High quality dog food
Cat Food sells for 45.22 and it is High quality cat food
Dog Toy sells for 12.5 and it is Now extra squeeky!
```
