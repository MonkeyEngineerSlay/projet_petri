class Place:
    def __init__(self, name, jetons):
        self.name = name
        self.jetons = jetons

class Arc:
    def __init__(self, input, cible, weight):
        self.input = input  # entré
        self.cible = cible  # nom transition ou place
        self.weight = weight 

class Transition:
    def __init__(self, name):
        self.name = name

class Petri:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.arcs = []

    def add_place(self, name, jetons):
        self.places[name] = Place(name, jetons)

    def add_transition(self, name):
        self.transitions[name] = Transition(name)

    def add_arc(self, input_name,cible_name, weight):
        input=self.places.get(input_name) or self.transitions.get(input_name)
        cible=self.places.get(cible_name) or self.transitions.get(cible_name)
        self.arcs.append(Arc(input, cible, weight))
    #vérifier si une transition est franchissable
    def is_enabled(self, transition_name):
        transition = self.transitions[transition_name]
        #vérifiier pour chaque arc s'il y a assez de jetons pour passer
        for arc in self.arcs:
            if arc.target == transition:
                if arc.source.tokens < arc.weight:
                    return False
        return True

    def fire(self, transition_name):
        if not self.is_enabled(transition_name):
            return False
        transition = self.transitions[transition_name]
        #retirer les jetons des places d'entrée
        for arc in self.arcs:
            if arc.target == transition:
                arc.source.tokens -= arc.weight
        #ajouter les jetons aux places de sortie
        for arc in self.arcs:
            if arc.source == transition:
                arc.target.tokens += arc.weight
        return True

petri = Petri()

petri.add_place("P1", 1)
petri.add_place("P2", 1)

#ARC
#arc1 = Arc("P1", "T1", 1)
#arc2 = Arc("T1", "P2", 1)

petri.add_transition("T1")

petri.add_arc("P1", "T1", 1)

print(petri.places)
print(petri.transitions)
print(petri.arcs)