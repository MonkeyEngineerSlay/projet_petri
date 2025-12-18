#model.py
from collections import deque, Counter # Counter est pour l'affichage "Multiset"

class Place:
    def __init__(self, name, tokens=None):
        self.name = name
        # Gestion CPN : On s'assure que c'est une liste
        if tokens is None:
            self.tokens = []
        elif isinstance(tokens, list):
            self.tokens = tokens
        else:
            self.tokens = [None] * int(tokens) if isinstance(tokens, int) else []

    def add_token(self, val):
        self.tokens.append(val)

class Transition:
    def __init__(self, name, guard=None):
        self.name = name
        self.guard = guard 

class Arc:
    def __init__(self, source, target, expression="x"):
        self.source = source
        self.target = target
        self.expression = expression 

class PetriNet:
    def __init__(self):
        self.places = {}
        self.transitions = {}
        self.arcs = []
        
        # Structures pour le graphe d'états (Logique de Mahdi)
        self.marking_to_id = {}
        self.id_to_marking = {}
        self.edges = []

    def add_place(self, name, tokens_list=None):
        self.places[name] = Place(name, tokens_list)

    def add_transition(self, name, guard=None):
        self.transitions[name] = Transition(name, guard)

    def add_arc(self, source_name, target_name, expression="x"):
        source = self.places.get(source_name) or self.transitions.get(source_name)
        target = self.places.get(target_name) or self.transitions.get(target_name)
        if source and target:
            self.arcs.append(Arc(source, target, expression))

    # --- LOGIQUE DE TIR CPN (La tienne) ---

    def get_input_arcs(self, transition):
        return [arc for arc in self.arcs if arc.target == transition]

    def get_output_arcs(self, transition):
        return [arc for arc in self.arcs if arc.source == transition]

    def is_enabled(self, transition_name):
        transition = self.transitions.get(transition_name)
        if not transition: return False
        
        input_arcs = self.get_input_arcs(transition)
        for arc in input_arcs:
            if not arc.source.tokens:
                return False
        return True

    def fire(self, transition_name):
        if not self.is_enabled(transition_name):
            return False
            
        transition = self.transitions[transition_name]
        input_arcs = self.get_input_arcs(transition)
        output_arcs = self.get_output_arcs(transition)
        binding = {} 

        # Consommation
        for arc in input_arcs:
            var_name = arc.expression
            if arc.source.tokens:
                token_val = arc.source.tokens.pop(0)
                binding[var_name] = token_val

        # Production
        for arc in output_arcs:
            var_name = arc.expression
            if var_name in binding:
                val_to_produce = binding[var_name]
                arc.target.tokens.append(val_to_produce)
            else:
                arc.target.tokens.append(var_name)
        return True

    # --- ANALYSE & GRAPHE (Logique de Mahdi ADAPTÉE CPN) ---
    def get_marking_tuple(self):
            """
            Génère une signature unique et hashable (tuple) de l'état actuel.
            Vital pour les clés de dictionnaire dans le graphe de reachability.
            """
            place_names = sorted(self.places.keys())
            marking_list = []
            
            for name in place_names:
                tokens = self.places[name].tokens
                
                # Si tokens est None ou un entier par erreur, on normalise en liste vide
                if tokens is None or isinstance(tokens, int):
                    safe_tokens = []
                else:
                    safe_tokens = tokens
                    
                # On convertit tout en string et on trie pour que ["A", "B"] == ["B", "A"]
                sorted_tokens = tuple(sorted(str(t) for t in safe_tokens))
                marking_list.append(sorted_tokens)
            
        return tuple(marking_list)
    def _load_marking_tuple(self, marking_tuple):
        """Restaure le réseau dans un état précis (Logique Mahdi)."""
        place_names = sorted(self.places.keys())
        for name, tokens_tuple in zip(place_names, marking_tuple):
            # On reconvertit le tuple en liste pour que le CPN puisse travailler
            self.places[name].tokens = list(tokens_tuple)

    def init_state_space_structures(self):
        self.marking_to_id = {}
        self.id_to_marking = {}
        self.edges = []

    def build_reachability_graph(self):
        """
        ALGORITHME DE MAHDI (BFS)
        Intégralement conservé, il fonctionne parfaitement une fois
        que get_marking_tuple est corrigé.
        """
        self.init_state_space_structures()

        # 1) marquage initial
        initial_marking = self.get_marking_tuple()
        self.marking_to_id[initial_marking] = 0
        self.id_to_marking[0] = initial_marking

        queue = deque([0])

        while queue:
            current_id = queue.popleft()
            current_marking = self.id_to_marking[current_id]

            # Remettre le réseau dans ce marquage
            self._load_marking_tuple(current_marking)

            # 2) Tester les transitions
            # On copie les clés pour itérer tranquillement
            t_names = list(self.transitions.keys())
            
            for t_name in t_names:
                # IMPORTANT : Recharger l'état avant CHAQUE test
                self._load_marking_tuple(current_marking)
                
                if self.is_enabled(t_name):
                    self.fire(t_name)
                    new_marking = self.get_marking_tuple()

                    # 3) Enregistrer
                    if new_marking not in self.marking_to_id:
                        new_id = len(self.marking_to_id)
                        self.marking_to_id[new_marking] = new_id
                        self.id_to_marking[new_id] = new_marking
                        queue.append(new_id)
                    else:
                        new_id = self.marking_to_id[new_marking]

                    self.edges.append((current_id, new_id, t_name))
        
        # Restauration finale pour affichage
        self._load_marking_tuple(self.id_to_marking[0])

    def get_reachability_as_strings(self):
        """Version 'Multiset' pour un affichage propre des couleurs."""
        lines = []
        lines.append(f"--- GRAPHE DE REACHABILITY ({len(self.id_to_marking)} états) ---")
        lines.append("")
        
        place_names = sorted(self.places.keys())
        
        for node_id, marking in self.id_to_marking.items():
            state_desc = []
            for place_name, tokens_tuple in zip(place_names, marking):
                if not tokens_tuple: continue
                # Compte les couleurs (ex: 2 Rouge)
                counts = Counter(tokens_tuple)
                token_str = ", ".join([f"{cnt} {col}" for col, cnt in counts.items()])
                state_desc.append(f"{place_name}: [{token_str}]")
            
            final_str = " | ".join(state_desc) if state_desc else "Vide"
            lines.append(f"État {node_id} : {final_str}")
            
        lines.append("")
        lines.append("TRANSITIONS :")
        for s, t, name in self.edges:
            lines.append(f"État {s} --{name}--> État {t}")
            
        return "\n".join(lines)

    def remove_node(self, name):
        if name in self.places: del self.places[name]
        elif name in self.transitions: del self.transitions[name]
        else: return False
        self.arcs = [arc for arc in self.arcs if arc.source.name != name and arc.target.name != name]
        return True

    def clear(self):
        self.places.clear()
        self.transitions.clear()
        self.arcs.clear()
