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
    def __init__(self, name, input_arc, output_arc):
        self.name = name
        self.input_arc = input_arc      # entré
        self.output_arc = output_arc

class Petri:
    def __init__(self):
        self.places = {}
        self.transitions = {}

    def add_place(self, name, jetons):
        self.places[name] = Place(name, jetons)

    def add_transition(self, name, input_arc, output_arc):
        self.transitions[name] = Transition(name, input_arc, output_arc)

petri = Petri()

petri.add_place("P1", 1)
petri.add_place("P2", 1)

#ARC
arc1 = Arc("P1", "T1", 1)
arc2 = Arc("T1", "P2", 1)

petri.add_transition("T1",[arc1],[arc2])


print(petri)
