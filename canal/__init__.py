
from greenlet import greenlet
import logging


log = logging.getLogger(__name__)


class TerminateNodeType(object):
    def __repr__(self):
        return "<TerminateNode>"


TerminateNode = TerminateNodeType()


class Graph:
    _nodes = None
    _edges = None
    _sources = None

    def __init__(self):
        self._edges = {}
        self._nodes = {}
        self._sources = []

    def add_source(self):
        feed_source = None
        def feed_source(value):
            log.debug("%r -> %r", value, feed_source)
            self._traverse_edges(feed_source, value)
        self._sources.append(feed_source)
        return feed_source

    def add_node(self, callable):
        routine = greenlet(callable)

        # Let the callable initialize itself and run until it
        # first tries to read a value.

        def inp():
            return_to = routine.parent
            while True:
                (value, return_to) = return_to.switch()
                if value is TerminateNode:
                    # End iteration and let the routine
                    # finish up.
                    log.debug("%r has been asked to terminate", callable)
                    return
                log.debug("%r recieved %r", callable, value)
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
        for source in self._sources:
            log.debug("Terminating nodes from source %r", source)
            self._terminate_recursively(source)

        # Check for zombies
        for node, routine in self._nodes.iteritems():
            if not routine.dead:
                raise ZombieNodeError("Node %r did not exit" % node)

        # Kill all of the nodes and edges so any further input
        # will fail, and we'll free the greenlet objects.
        self._nodes = {}
        self._edges = {}
        self._sources = []

    def _terminate_recursively(self, source_node):
        child_nodes = self._edges.get(source_node)
        if child_nodes is not None:
            self._traverse_edges(source_node, TerminateNode)
            for node in child_nodes:
                self._terminate_recursively(node)

    def _traverse_edges(self, source_node, value):
        try:
            target_nodes = self._edges[source_node]
        except KeyError, ex:
            raise SinkEmitError("Sink node %r attempted to emit a value")
        for node in target_nodes:
            routine = self._nodes[node]
            log.debug("%r -> %r -> %r", source_node, value, node)
            routine.switch((value, greenlet.getcurrent()))


class SinkEmitError(Exception):
    pass


class ZombieNodeError(Exception):
    pass
