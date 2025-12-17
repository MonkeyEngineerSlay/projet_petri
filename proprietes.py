# verification des proprietes.py
from collections import defaultdict


def construire_graphe_reachability(net):
    graphe = defaultdict(list)

    for src, tgt, t_name in net.edges:
        m_src = net.id_to_marking[src]
        m_tgt = net.id_to_marking[tgt]
        graphe[m_src].append((t_name, m_tgt))

    for m in net.id_to_marking.values():
        graphe.setdefault(m, [])


    return graphe


def verifier_deadlock(graphe):
    return [m for m, arcs in graphe.items() if len(arcs) == 0]


def verifier_bornitude(graphe, max_tokens=1):
    for marquage in graphe:
        if any(j > max_tokens for j in marquage):
            return False
    return True


def verifier_conservation(graphe):
    marquages = list(graphe.keys())
    somme_ref = sum(marquages[0])
    return all(sum(m) == somme_ref for m in marquages)


def verifier_vivacite_faible(graphe):
    transitions = set()
    for arcs in graphe.values():
        for t, _ in arcs:
            transitions.add(t)
    return len(transitions) > 0


def analyser_reseau(net):
    net.build_reachability_graph()
    graphe = construire_graphe_reachability(net)

    return {
        "Deadlocks": verifier_deadlock(graphe),
        "Bornitude": "OK" if verifier_bornitude(graphe) else "Non",
        "Conservation": "OK" if verifier_conservation(graphe) else "Non",
        "Vivacité (faible)": "OK" if verifier_vivacite_faible(graphe) else "Non",
    }
