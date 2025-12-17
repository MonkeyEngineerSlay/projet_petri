# test_petri.py
import pytest
from model import PetriNet
from analysis import PetriAnalyzer

def test_creation():
    """Vérifie qu'on peut créer des places et transitions"""
    net = PetriNet()
    net.add_place("P1", 1)
    net.add_transition("T1")
    net.add_arc("P1", "T1")
    
    assert "P1" in net.places
    assert net.places["P1"].tokens == 1
    assert len(net.arcs) == 1

def test_firing():
    """Vérifie la logique de tir"""
    net = PetriNet()
    net.add_place("P1", 1)
    net.add_place("P2", 0)
    net.add_transition("T1")
    
    net.add_arc("P1", "T1")
    net.add_arc("T1", "P2")
    
    # Avant tir
    assert net.places["P1"].tokens == 1
    assert net.places["P2"].tokens == 0
    assert net.is_enabled("T1") == True
    
    # Tir
    success = net.fire("T1")
    
    # Après tir
    assert success == True
    assert net.places["P1"].tokens == 0
    assert net.places["P2"].tokens == 1
    assert net.is_enabled("T1") == False

def test_deadlock_analysis():
    """Vérifie si l'analyseur détecte un blocage"""
    net = PetriNet()
    # P1 -> T1 -> P2 (P2 ne va nulle part, c'est un état final)
    net.add_place("P1", 1)
    net.add_place("P2", 0)
    net.add_transition("T1")
    net.add_arc("P1", "T1")
    net.add_arc("T1", "P2")
    
    analyzer = PetriAnalyzer(net)
    props = analyzer.analyze_properties()
    
    # Il doit y avoir 2 états : (P1=1, P2=0) et (P1=0, P2=1)
    assert props["state_count"] == 2
    # L'état final (P1=0, P2=1) est un deadlock car T1 ne peut plus tirer
    assert len(props["deadlocks"]) == 1

if __name__ == "__main__":
    # Permet de lancer le test sans pytest installé via "python test_petri.py"
    try:
        test_creation()
        test_firing()
        test_deadlock_analysis()
        print("Tous les tests sont passés avec SUCCÈS !")
    except AssertionError as e:
        print(f"ÉCHEC du test : {e}")