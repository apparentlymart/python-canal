
import unittest
from canal import Graph

class TestGraph(unittest.TestCase):

    def test_simple(self):
        graph = Graph()
        source = graph.add_source()

        items = []
        terminated = [ False ]
        def add_items(inp, outp):
            for value in inp:
                items.append(len(value))
            terminated[0] = True

        graph.add_node(add_items)
        graph.add_edge(source, add_items)

        source("hello")
        source("pizza")
        source("cheese")
        source("2")
        source("blahblahblah")
        graph.terminate()

        self.assertEqual(items, [
            5, 5, 6, 1, 12,
        ], "Node yielded expected items")
        self.assertTrue(terminated[0], "Node terminated")
