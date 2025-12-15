# (Ce fichier contient la logique : Classes Place, Transition, Arc, PetriNet)

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
