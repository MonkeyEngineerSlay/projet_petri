import unittest
import os, sys

# Permet à python de trouver model.py même si on lance le test depuis ailleurs
sys.path.append(os.path.dirname(__file__))

from model import PetriNet

class TestReachability(unittest.TestCase):
    
    def test_simple_cpn_propagation(self):
        """
        Teste le déplacement d'un jeton 'Rouge' de P1 vers P2.
        """
        net = PetriNet()

        # --- 1. SETUP CPN (Listes au lieu d'entiers) ---
        # Place 1 contient un jeton "Rouge"
        net.add_place("p1", ["Rouge"])
        # Place 2 est vide
        net.add_place("p2", [])

        net.add_transition("t1")

        # --- 2. ARCS (Variables au lieu de poids) ---
        # L'arc prend la variable "x" depuis p1 et dépose "x" dans p2
        net.add_arc("p1", "t1", "x")
        net.add_arc("t1", "p2", "x")

        # --- 3. GÉNÉRATION DU GRAPHE ---
        net.build_reachability_graph()

        print("\n=== Test 1 : Propagation Simple ===")
        for node_id, marking in net.id_to_marking.items():
            print(f"État {node_id}: {marking}")
        
        # --- 4. ASSERTIONS (Vérifications) ---
        
        # Le graphe doit contenir au moins 2 états (État initial -> État final)
        self.assertGreaterEqual(len(net.id_to_marking), 2)

        # L'état initial doit être présent : P1=('Rouge',), P2=()
        # Note : tes marquages sont des tuples de tuples triés
        initial_marking = (('Rouge',), ())
        self.assertIn(initial_marking, net.marking_to_id)

        # L'état final doit être présent : P1=(), P2=('Rouge',)
        final_marking = ((), ('Rouge',))
        self.assertIn(final_marking, net.marking_to_id)


    def test_multiple_tokens_sequence(self):
        """
        Teste une séquence avec plusieurs jetons différents (A et B).
        Vérifie que le modèle consomme bien tout jusqu'à la fin.
        """
        net = PetriNet()
        
        # On initialise avec deux jetons distincts
        net.add_place("Start", ["A", "B"])
        net.add_place("End", [])
        net.add_transition("T")

        net.add_arc("Start", "T", "v")
        net.add_arc("T", "End", "v")

        net.build_reachability_graph()

        print("\n=== Test 2 : Séquence A, B ===")
        for s, d, t in net.edges:
            print(f"État {s} --{t}--> État {d}")

        # On vérifie l'état final où tout est arrivé dans "End"
        # Les tuples étant triés dans ta fonction get_marking_tuple :
        # Start = (), End = ('A', 'B')
        final_state = ((), ('A', 'B'))
        
        self.assertIn(final_state, net.marking_to_id)

if __name__ == "__main__":
    unittest.main()