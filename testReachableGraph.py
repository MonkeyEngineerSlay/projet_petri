import unittest

import os, sys
sys.path.append(os.path.dirname(__file__))

from petri_model import PetriNet


def reachability_graph():
    net = PetriNet()
    net.add_place("p1", 1)
    net.add_place("p2", 0)
    net.add_transition("t1")
    net.add_arc("p1", "t1", 1)
    net.add_arc("t1", "p2", 1)

    net.build_reachability_graph()
    return net


class TestReachability(unittest.TestCase):
    def test_simple_net(self):
        net=reachability_graph()

        print("=== États (nœuds) ===")
        for node_id, marking in net.id_to_marking.items():
            print(f"{node_id}: {marking}")

        print("=== Arcs ===")
        for source, target, t_name in net.edges:
            print(f"{source} --{t_name}--> {target}")


        self.assertEqual(len(net.id_to_marking), 2)
        self.assertIn((1, 0), net.marking_to_id)
        self.assertIn((0, 1), net.marking_to_id)
        self.assertIn((0, 1, "t1"), net.edges)

if __name__ == "__main__":
    unittest.main()
