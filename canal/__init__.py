
from greenlet import greenlet


TerminateNode = object()


class Graph:
    _nodes = None
    _edges = None

    def __init__(self):
        self._edges = {}
        self._nodes = {}

    def add_source(self):
        feed_source = None
        def feed_source(value):
            self._traverse_edges(feed_source, value)
        return feed_source

    def add_node(self, callable):
        routine = greenlet(callable)

        # Let the callable initialize itself and run until it
        # first tries to read a value.

        def inp():
            while True:
                current_routine = greenlet.getcurrent()
                value = current_routine.parent.switch()
                if value is TerminateNode:
                    # End iteration and let the routine
                    # finish up.
                    return
                yield value

        def outp(value):
            self._traverse_edges(callable, value)

        routine.switch(inp(), outp)

        if routine.dead:
            raise ValueError(
                "Node callable %r exited without processing any values." % (
                    callable
                )
            )

        self._nodes[callable] = routine

    def add_edge(self, source_node, target_node):
        try:
            target_nodes = self._edges[source_node]
        except KeyError, ex:
            self._edges[source_node] = []
            target_nodes = self._edges[source_node]
        target_nodes.append(target_node)

    def terminate(self):
        for node, routine in self._nodes.iteritems():
            routine.switch(TerminateNode)
            if not routine.dead:
                raise ZombieNodeError("Node %r did not exit" % node)
        # Kill all of the nodes and edges so any further input
        # will fail, and we'll free the greenlet objects.
        self._nodes = {}
        self._edges = {}

    def _traverse_edges(self, source_node, value):
        try:
            target_nodes = self._edges[source_node]
        except KeyError, ex:
            raise SinkEmitError("Sink node %r attempted to emit a value")
        for node in target_nodes:
            routine = self._nodes[node]
            routine.switch(value)


class SinkEmitError(Exception):
    pass


class ZombieNodeError(Exception):
    pass
