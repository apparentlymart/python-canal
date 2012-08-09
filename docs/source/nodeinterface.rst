Node Interface
==============

The node interface is a lightweight convention for stream processing nodes.

The node interface is to a stream processing system as a as Webserver Gateway
Interface (WSGI) app is to a a web server: it allows you to write stream
processing nodes in a convenient, framework-agnostic way and then use these
nodes in any stream processing system that supports this protocol.

The node interface consists of two concepts: node functions and node
constructors.

Node Functions
--------------

A node function is the actual implementation of the node. It is a callable
that takes two positional arguments: an iterable and a callable, respectively.

The iterable, conventionally called `inp`, provides the input stream. The
callable, conventionally called `outp`, writes to the output stream.
The body of a node function must iterate over the entire input stream using
the standard iterator protocol, and may call `outp` at any time to emit
a value.

Here is a simple example of a node function that just adds 1 to what it
receives (which had better be something that can have an integer added to it)
and re-emits it, generating exactly one output value for each input value.

.. code-block:: python

   def add_one(inp, outp):
       for value in inp:
           outp(value + 1)

In this simple case the entire body of the function is the for loop, but
for more complex cases a node function can do initialization before the
for loop (for example, allocating resources that will be needed during
processing) and finalization after the for loop.

For example, a node function that incorporates some kind of buffer to aggregate
together multiple input values into a single output value might include some
code after the loop to flush any remaining values in the buffer before
terminating.

Node functions should expect to process many values before terminating. When
running in an online stream processing system the stream is often logically
infinite and terminates only for operational reasons such as the system
being restarted for code upgrades.

Node Constructors
-----------------

A node constructor is simply a callable that returns a node function. It is
a convenient way to provide reusable, parameterized node implementations.
The functions in :py:mod:`canal.nodes` are node constructors.

The contract for a node constructor is just that it must return a different
callable object each time it is run. It must not return the same object
over multiple calls, since the callable object also represents the identity
of the node and thus the same node function cannot exist more than once in a
graph.

Therefore a common pattern is for a node constructor to create and return
a lexical closure from the constructor's parameters. Here's a variation of
the above node function example with a constructor that allows the amount
to be added to be customized:

.. code-block:: python

    def add(amount):
        def add_impl(inp, outp):
            for value in inp:
                outp(value + amount)
        return add_impl

However, since the contract is just a callable that returns a callable,
you can write this as a class if you prefer:

.. code-block:: python

    class add(object):

        def __init__(amount):
            self.amount = amount

        def __call__(inp, outp):
            for value in inp:
                outp(value + self.amount)

In the above case, the class itself is the node constructor and instances
of that class are node functions, but you can also think of it as the
class's constructor being the node constructor and the ``__call__`` function
being the node function.

Considerations for Stream Processing System Implementors
--------------------------------------------------------

If you are building a stream processing system or building Python bindings to
an existing stream processing system then you will be _calling_ rather than
implementing node functions.

As a caller of a node function it is your responsibility to provide an
appropriate iterable for the input and an appropriate callable as an interface
to the output.

The node function is iterating over the input for the entirety of its runtime,
so from the perspective of the node function it must seem that the iterator
blocks until new data is available.

If each node is running in its own process or thread then it will be simplest
to actually block on whatever socket or other data source is providing new
values to be processed. If true blocking is not acceptable for a particular
implementation then a coroutine abstraction like ``greenlet`` can be used
to provide the interface within a single thread. This is the technique
used by the reference implementation :py:class:`canal.Graph` to run the
entire graph in a single OS thread.

When implementing the output callable it is important to ensure that control
returns to the node function so that it can complete its loop and block on
the next iteration. This is straightforward in the one-thread-per-node scenario
but in a coroutine implementation it is important to return control to the
different coroutines in the correct order to ensure correct operation.
