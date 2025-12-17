# (Ce fichier contient la logique : Classes Place, Transition, Arc, PetriNet)
from collections import deque


class Place:
    def __init__(self, name, tokens=0):
        self.name = name
        self.tokens = tokens

class Transition:
    def __init__(self, name):
        self.name = name

class Arc:
    def __init__(self, source, target, weight=1):
        self.source = source
        self.target = target
        self.weight = weight

class PetriNet: # C'est ce nom que interface.py cherche
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.arcs = []

    def add_place(self, name, tokens=0):
        self.places[name] = Place(name, tokens)

    def add_transition(self, name):
        self.transitions[name] = Transition(name)

    def add_arc(self, source_name, target_name, weight=1):
        # On cherche l'objet dans les places OU les transitions
        source = self.places.get(source_name) or self.transitions.get(source_name)
        target = self.places.get(target_name) or self.transitions.get(target_name)
        
        if source and target:
            self.arcs.append(Arc(source, target, weight))
        else:
            print(f"Erreur: Impossible de créer l'arc {source_name} -> {target_name}")

    def is_enabled(self, transition_name):
        transition = self.transitions.get(transition_name)
        if not transition: 
            return False
            
        for arc in self.arcs:
            if arc.target == transition:
                if arc.source.tokens < arc.weight:
                    return False
        return True

    def fire(self, transition_name):
        if not self.is_enabled(transition_name):
            return False
        
        transition = self.transitions[transition_name]
        
        # 1. Consommer les jetons
        for arc in self.arcs:
            if arc.target == transition:
                arc.source.tokens -= arc.weight
                
        # 2. Produire les jetons
        for arc in self.arcs:
            if arc.source == transition:
                arc.target.tokens += arc.weight
                
        return True

    def get_marking_tuple(self):
        #tuple de marquages
        place_names = sorted(self.places.keys())
        return tuple(self.places[name].tokens for name in place_names)

    def init_state_space_structures(self):
        self.marking_to_id = {}  # {marquage_tuple: id_entier}
        self.id_to_marking = {}  # {id_entier: marquage_tuple}
        self.edges = []  # [(id_source, id_cible, nom_transition)]

    def build_reachability_graph(self):
        self.init_state_space_structures()

        # 1) marquage initial
        initial_marking = self.get_marking_tuple()
        self.marking_to_id[initial_marking] = 0
        self.id_to_marking[0] = initial_marking

        queue = deque([0])  # ids à explorer

        while queue:
            current_id = queue.popleft()
            current_marking = self.id_to_marking[current_id]

            # remettre le réseau dans ce marquage
            self._load_marking_tuple(current_marking)

            # 2) pour chaque transition, tester is_enabled et tirer
            for t_name in self.transitions.keys():
                if self.is_enabled(t_name):
                    # copier le marquage courant avant tir
                    saved_marking = self.get_marking_tuple()

                    # tirer
                    self.fire(t_name)
                    new_marking = self.get_marking_tuple()

                    # remettre l'ancien marquage pour continuer l'exploration
                    self._load_marking_tuple(saved_marking)

                    # 3) enregistrer le nœud et l'arête
                    if new_marking not in self.marking_to_id:
                        new_id = len(self.marking_to_id)
                        self.marking_to_id[new_marking] = new_id
                        self.id_to_marking[new_id] = new_marking
                        queue.append(new_id)
                    else:
                        new_id = self.marking_to_id[new_marking]

                    self.edges.append((current_id, new_id, t_name))

    def _load_marking_tuple(self, marking_tuple):
        place_names = sorted(self.places.keys())
        for name, tokens in zip(place_names, marking_tuple):
            self.places[name].tokens = tokens

    def get_reachability_as_strings(self):
        lines = []
        lines.append("États (id : marquage) :")
        for node_id, marking in self.id_to_marking.items():
            lines.append(f"{node_id} : {marking}")
        lines.append("")
        lines.append("Transitions (source --t--> cible) :")
        for s, t, name in self.edges:
            lines.append(f"{s} --{name}--> {t}")
        return "\n".join(lines)



