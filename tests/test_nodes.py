
import unittest
import logging
from canal import Graph


log = logging.getLogger(__name__)


class TestNodes(unittest.TestCase):

    def test_grep(self):
        from canal.nodes import grep
        self.assertNodeBehavior(
            grep(lambda x : x > 5),
            [
                1, 3, 5, 7, 9, 2, 4, 6, 8, 10,
            ],
            [
                7, 9, 6, 8, 10,
            ],
        )


    def test_transform(self):
        from canal.nodes import transform
        self.assertNodeBehavior(
            transform(lambda x : x + 3),
            [
                1, 3, 5, 7, 9, 2, 4, 6, 8, 10,
            ],
            [
                4, 6, 8, 10, 12, 5, 7, 9, 11, 13,
            ],
        )


    def test_uniq(self):
        from canal.nodes import uniq
        self.assertNodeBehavior(
            uniq(),
            [
                None, None, 1, 2, 3, 3, 4, 5, 6, None, 7, 7, 7, 7, 10, None,
            ],
            [
                None, 1, 2, 3, 4, 5, 6, None, 7, 10, None,
            ],
        )


    def test_aggregate(self):
        from canal.nodes import aggregate
        node = aggregate(
            key_func=lambda x : x[0],
            close_func=lambda a : a[-1][1] == "end",
        )
        input = [
            (1, "start"),
            (1, "end"),
            (1, "start"),
            (1, "middle"),
            (1, "end"),
            (3, "start"),
            (2, "start"),
            (3, "middle"),
            (2, "end"),
            (3, "end"),
            (1, "end"),
            (5, "start"), # never closed, so will leak
            (4, "end"),
        ]
        expected_output = [
            [
                (1, "start"),
                (1, "end"),
            ],
            [
                (1, "start"),
                (1, "middle"),
                (1, "end"),
            ],
            [
                (2, "start"),
                (2, "end"),
            ],
            [
                (3, "start"),
                (3, "middle"),
                (3, "end"),
            ],
            [
                (1, "end"),
            ],
            [
                (4, "end"),
            ],
        ]
        self.assertNodeBehavior(node, input, expected_output)

    def test_json_encode(self):
        from canal.nodes import json_encode
        self.assertNodeBehavior(
            json_encode(indent=4),
            [{},[1],True],
            ["{}", "[\n    1\n]", "true"],
        )

    def test_json_decode(self):
        from canal.nodes import json_decode
        self.assertNodeBehavior(
            json_decode(),
            ["{}", "[]", "true"],
            [{},[],True],
        )

    def test_sink_to_callable(self):
        from canal.nodes import sink_to_callable
        graph = Graph()
        source = graph.add_source()
        values = []
        def func(value):
            values.append(value)
        sink = sink_to_callable(func)
        graph.add_node(sink)
        graph.add_edge(source, sink)
        for value in (1, 2, 3, 4, 5):
            source(value)
        self.assertEquals(values, [1, 2, 3, 4, 5])

    def test_sink_to_file(self):
        from canal.nodes import sink_to_file
        from StringIO import StringIO

        linef = StringIO()
        spacef = StringIO()

        graph = Graph()
        source = graph.add_source()

        linesink = sink_to_file(linef)
        spacesink = sink_to_file(spacef, separator=" ")
        graph.add_node(linesink)
        graph.add_node(spacesink)
        graph.add_edge(source, linesink)
        graph.add_edge(source, spacesink)

        test_values = ("a", "b", "c", "d", "e")

        for value in test_values:
            source(value)

        self.assertEquals(linef.getvalue(), "\n".join(test_values + ('',)))
        self.assertEquals(spacef.getvalue(), " ".join(test_values + ('',)))


    def assertNodeBehavior(self, node, input, expected_output):
        harness = NodeHarness(node)
        harness.simple_test(self, input, expected_output)

    def feedToSink(self, sink, input):
        graph = Graph()
        source = graph.add_source()
        graph.add_node(sink)
        graph.


class NodeHarness(object):
    """
    Make a simple graph from the provided node and attach a sink to it that
    logs its input to an array. This factors out a bunch of boilerplate
    around testing nodes that have both input and output. (i.e. not sinks)
    """

    def __init__(self, node):
        graph = Graph()
        source = graph.add_source()
        graph.add_node(node)
        output = []
        def sink(inp, outp):
            log.debug("Sink initializing")
            for value in inp:
                log.debug("Sink got %r", value)
                output.append(value)
            log.debug("Sink terminating")
        graph.add_node(sink)

        graph.add_edge(source, node)
        graph.add_edge(node, sink)

        self.output = output
        self.source = source
        self.graph = graph

    def feed(self, iterable):
        for value in iterable:
            log.debug("Feeding %r", value)
            self.source(value)
        log.debug("Done feeding")

    def simple_test(self, test_case, input, expected_output):
        self.feed(input)
        test_case.assertEqual(self.output, expected_output)
        self.terminate()

    def terminate(self):
        log.debug("Terminating")
        self.graph.terminate()
