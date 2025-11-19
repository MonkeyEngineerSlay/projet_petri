class Place:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

class Transition:
    def __init__(self, input, output, name):
        self.name=name
        self.input = input
        self.output= output

class Petri:
    def __init__(self, places, transitions):
        self.places = {}
        self.transitions = {}

    def add_place(self, name, weight):
        self.places[name] = Place(name, weight)

    def add_transition(self, name, input, output):
        self.transitions[name] = Transition(name, input, output)

places={1:Place(1,2),2:Place(2,4),}
print(places)

transitions={1}



