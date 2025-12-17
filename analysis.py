# analysis.py
from collections import deque

class PetriAnalyzer:
    def __init__(self, model):
        self.model = model

    def build_reachability_graph(self):
        """
        Construit le Graphe d'Accessibilité.
        Retourne :
            - graph : Dictionnaire {Etat_source: [(Transition, Etat_cible), ...]}
            - states : Liste de tous les états rencontrés
        """
        # 1. Sauvegarder l'état initial pour le remettre à la fin
        initial_marking = self.model.get_marking()
        
        # Structures pour l'exploration
        # graph: { Etat : [ (NomTransition, NouvelEtat), ... ] }
        graph = {}
        # visited: Set des états déjà explorés pour éviter les boucles infinies
        visited = set()
        # queue: File d'attente pour le parcours en largeur (BFS)
        queue = deque([initial_marking])
        
        visited.add(initial_marking)

        while queue:
            current_marking = queue.popleft()
            
            # On charge l'état dans le modèle pour voir ce qui est possible
            self.model.set_marking(current_marking)
            
            # On initialise la liste des voisins dans le graphe
            if current_marking not in graph:
                graph[current_marking] = []

            # Quelles transitions peut-on tirer ici ?
            enabled_trans = self.model.get_enabled_transitions()
            
            # Si aucune transition n'est possible -> C'est un DEADLOCK (blocage)
            
            for t_name in enabled_trans:
                # 1. Tirer la transition (Simuler)
                self.model.fire(t_name)
                
                # 2. Capturer le nouvel état
                new_marking = self.model.get_marking()
                
                # 3. Ajouter l'arc au graphe
                graph[current_marking].append((t_name, new_marking))
                
                # 4. Si c'est un nouvel état, on l'ajoute à la file
                if new_marking not in visited:
                    visited.add(new_marking)
                    queue.append(new_marking)
                
                # 5. Retour arrière (Backtrack) pour tester la prochaine transition
                self.model.set_marking(current_marking)

        # On remet le modèle dans son état d'origine
        self.model.set_marking(initial_marking)
        
        return graph, visited

    def analyze_properties(self):
        """Analyse le graphe pour trouver deadlocks et bornitude"""
        graph, states = self.build_reachability_graph()
        
        deadlocks = []
        is_bounded = True # Simplifié (suppose borné si l'algo termine)
        max_tokens = 0

        for state in states:
            # Vérification des bornes (somme des jetons)
            total_tokens = sum(tokens for name, tokens in state)
            if total_tokens > max_tokens:
                max_tokens = total_tokens
            
            # Vérification Deadlock : Si l'état n'a pas de sortants dans le graphe ou liste vide
            if state not in graph or len(graph[state]) == 0:
                deadlocks.append(state)

        return {
            "state_count": len(states),
            "deadlocks": deadlocks,
            "bounded": True, # Si la boucle while finit, c'est borné (dans cette implémentation simple)
            "max_tokens_seen": max_tokens
        }