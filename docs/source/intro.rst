Introduction to Stream Processing
=================================

Stream processing, at least in the sense we will use it here, refers to
the process of taking a potentially-infinite stream of input values and
producing a corresponding set of output values via arbitrary per-input
operations.

The UNIX commands `grep`, `uniq`, `cut`, `tr` and `sed` are familiar examples
of stream processing: they read a stream of strings separated by newlines and
emit a stream of strings separated by newlines that is related somehow to the
input. Because these tools share a common interface they can be combined
arbitrarily to perform higher-level operations, feeding the output of one
into the next. The shell provides a syntax for concisely describing chains of
stream-processing commands starting with a source command:

.. code-block:: bash

   $ some_program | cut -f 2 | grep "foo"

This set of tools is a specific application of stream processing aimed at
wrangling the output of line-based UNIX programs.

A general way to think about this pattern is as a directed acyclic graph whose
nodes are either sources, which produce stream items, sinks, which consume
stream items, or transformation nodes that both consume and emit items.

Canal is an application of this stream processing methodology to streams of
Python values. It defines an interface convention for implementing the nodes
of the graph, provides a simple graph implementation that uses this convention
to interact with nodes, and provides a set of generic node implementations that
could be useful in a number of applications.

The graph implementation included in this distribution can be thought of as
a reference implementation of interacting with stream processing nodes that
comply with the interface convention. The interface convention is intended to
be applicable to other stream processing frameworks which may provide a better
implementation including distributed processing.

Here is a simple (and somewhat contrived) example of using stream processing
to process lines from stdin using some of the simple node implementations
provided in :py:mod:`canal.nodes` and the included graph implementation:

.. code-block:: python

    import canal
    import canal.nodes
    from sys import stdin, stdout

    graph = canal.Graph()

    # Declare a source node and obtain a callable that will feed items
    # into the graph via this source.
    source = graph.add_source()

    # Construct our other nodes
    split_node = canal.nodes.transform(lambda value : value.split())
    json_encode_node = canal.nodes.json_encode()
    sink = canal.nodes.sink_to_file(stdout)

    # Add the nodes to the graph
    graph.add_node(split_node)
    graph.add_node(json_encode_node)
    graph.add_node(sink)

    # Add edges to the graph
    graph.add_edge(source, split_node)
    graph.add_edge(split_node, json_encode_node)
    graph.add_edge(json_encode_node, sink)

    # Now feed the lines from stdin into the graph
    for line in stdin:
        source(line)

