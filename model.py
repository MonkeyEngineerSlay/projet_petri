# model.py
# Ce fichier gère la logique pure du Réseau de Petri (Mathématiques)

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

class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.arcs = []

    def add_place(self, name, tokens=0):
        self.places[name] = Place(name, tokens)

    def add_transition(self, name):
        self.transitions[name] = Transition(name)

    def add_arc(self, source_name, target_name, weight=1):
        # Récupération des objets (soit Place, soit Transition)
        source = self.places.get(source_name) or self.transitions.get(source_name)
        target = self.places.get(target_name) or self.transitions.get(target_name)
        
        # Vérification 1 : Les deux existent
        if not source or not target:
            return False

        # Vérification 2 : On ne relie pas Place-Place ou Transition-Transition
        if type(source) == type(target):
            return False 

        self.arcs.append(Arc(source, target, weight))
        return True

    def remove_node(self, name):
        """Supprime une Place ou une Transition et nettoie les arcs associés"""
        if name in self.places:
            del self.places[name]
        elif name in self.transitions:
            del self.transitions[name]
        else:
            return False # L'objet n'existe pas

        # On garde seulement les arcs qui NE sont PAS connectés à l'objet supprimé
        self.arcs = [arc for arc in self.arcs 
                     if arc.source.name != name and arc.target.name != name]
        return True

    def clear(self):
        """Vide entièrement le réseau (utilisé avant le chargement JSON)"""
        self.places.clear()
        self.transitions.clear()
        self.arcs.clear()

    def is_enabled(self, transition_name):
        """Vérifie si une transition peut être tirée"""
        t = self.transitions.get(transition_name)
        if not t: return False

        # On regarde tous les arcs qui entrent dans la transition
        for arc in self.arcs:
            if arc.target == t:
                # Si la place source n'a pas assez de jetons par rapport au poids
                if arc.source.tokens < arc.weight:
                    return False
        return True

    def fire(self, transition_name):
        """Exécute le tir d'une transition"""
        if not self.is_enabled(transition_name):
            return False
        
        t = self.transitions.get(transition_name)

        # 1. Consommer les jetons (Entrée)
        for arc in self.arcs:
            if arc.target == t:
                arc.source.tokens -= arc.weight

        # 2. Produire les jetons (Sortie)
        for arc in self.arcs:
            if arc.source == t:
                arc.target.tokens += arc.weight
            
        return True

    # --- MÉTHODES POUR L'ANALYSE (Section 2.2) ---

    def get_marking(self):
        """Retourne l'état actuel sous forme de tuple hashable ((P1, 1), (P2, 0)...)"""
        # On trie par nom pour garantir que le même état donne toujours le même tuple
        return tuple(sorted((name, p.tokens) for name, p in self.places.items()))

    def set_marking(self, marking):
        """Force le réseau dans un état précis (pour explorer les hypothèses)"""
        # marking est une liste ou tuple de paires (nom, jetons)
        for name, tokens in marking:
            if name in self.places:
                self.places[name].tokens = tokens

    def get_enabled_transitions(self):
        """Retourne la liste des noms de toutes les transitions activables dans l'état actuel"""
        return [t_name for t_name in self.transitions if self.is_enabled(t_name)]