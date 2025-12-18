#editor.py
import json
import tkinter.filedialog as filedialog

class PetriEditor:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = "PLACE"
        self.selected_source = None
        
        # Variables pour le déplacement (Drag & Drop)
        self.drag_item_name = None 

    def set_mode(self, mode):
        self.mode = mode
        self.selected_source = None
        self.drag_item_name = None
        
        info = f"Mode: {mode}"
        if mode == "MOVE":
            info = "Mode: DÉPLACEMENT (Glissez-déposez les objets)"
        elif mode == "REACH":    
            self.view.show_reachability_graph()  # ← LIGNE 1
            return
        elif mode == "SAVE":
            self.save_project()
            return
        elif mode == "LOAD":
            self.load_project()
            return
            
        self.view.update_mode_label(info)

    def handle_click(self, x, y, item_name):
        """Gestion des clics gauche sur le canvas selon le mode."""
        
        # --- MODE PLACE (CPN : Avec Constructeur de Jetons) ---
        if self.mode == "PLACE":
            # On appelle le nouveau menu graphique de l'interface
            tokens = self.view.ask_token_builder()
            
            # Si l'utilisateur annule, on met une liste vide par défaut
            if tokens is None: 
                tokens = [] 

            name = f"P{len(self.model.places)}"
            self.model.add_place(name, tokens)
            self.view.draw_place_visual(x, y, name, tokens)

        # --- MODE TRANSITION ---
        elif self.mode == "TRANSITION":
            name = f"T{len(self.model.transitions)}"
            self.model.add_transition(name)
            self.view.draw_transition_visual(x, y, name)

        # --- MODE ARC (CPN : Avec Variable) ---
        elif self.mode == "ARC":
            if not item_name: return
            if self.selected_source is None:
                # Premier clic : sélection de la source
                self.selected_source = item_name
                self.view.update_mode_label(f"ARC: de {item_name} vers... ?")
                return

            source = self.selected_source
            target = item_name

            # On demande le nom de la variable (ex: "x")
            var_name = self.view.ask_arc_variable()
            if var_name is None:
                # Annulation
                self.selected_source = None
                self.view.update_mode_label("ARC (Source ?)")
                return

            # Création de l'arc dans le modèle et la vue
            self.model.add_arc(source, target, var_name)
            self.view.draw_arc_visual(source, target, var_name)

            # Reset pour le prochain arc
            self.selected_source = None
            self.view.update_mode_label("ARC (Source ?)")

        # --- MODE TIRER (Simulation) ---
        elif self.mode == "FIRE":
            if item_name and item_name.startswith("T"):
                # Si le tir réussit, on rafraîchit l'affichage des jetons
                if self.model.fire(item_name):
                    self.view.refresh_tokens()
        
        # --- MODE DÉPLACEMENT ---
        elif self.mode == "MOVE":
            if item_name:
                self.drag_item_name = item_name

        # --- MODE ANALYSE (Reachability) ---
        elif self.mode == "REACH":
            from proprietes import analyser_reseau

            resultats = analyser_reseau(self.model)
            texte = self.model.get_reachability_as_strings()

            texte += "\n\n=== Analyse des propriétés ===\n"
            for k, v in resultats.items():
                texte += f"{k} : {v}\n"

            self.view.show_text_window("Reachability & Propriétés", texte)

            # Construction et affichage du graphe
            self.model.build_reachability_graph()
            text = self.model.get_reachability_as_strings()
            self.view.show_text_window("Graphe de reachability", text)

        # --- MODE SUPPRESSION ---
        elif self.mode == "DELETE":
            if item_name:
                if self.model.remove_node(item_name):
                    self.view.delete_visual(item_name)


    def handle_drag(self, x, y):
        """Appelé quand la souris bouge avec le bouton enfoncé"""
        if self.mode == "MOVE" and self.drag_item_name:
            self.view.move_object(self.drag_item_name, x, y)

    def handle_release(self):
        """Appelé quand on relâche le bouton de la souris"""
        if self.mode == "MOVE":
            self.drag_item_name = None

    def save_project(self):
        """Sauvegarde au format JSON compatible CPN"""
        data = {"places": [], "transitions": [], "arcs": []}

        # Sauvegarde des Places (avec la liste des tokens colorés)
        for name, place in self.model.places.items():
            x, y = self.view.name_to_coords.get(name, (0, 0))
            data["places"].append({
                "name": name, 
                "tokens": place.tokens, # JSON gère nativement les listes ["Rouge", "Bleu"]
                "x": x, 
                "y": y
            })

        # Sauvegarde des Transitions
        for name, trans in self.model.transitions.items():
            x, y = self.view.name_to_coords.get(name, (0, 0))
            data["transitions"].append({"name": name, "x": x, "y": y})

        # Sauvegarde des Arcs (avec variable/expression)
        for arc in self.model.arcs:
            data["arcs"].append({
                "source": arc.source.name, 
                "target": arc.target.name, 
                "expression": arc.expression 
            })

        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            with open(filename, 'w') as f: json.dump(data, f, indent=4)
            print(f"Sauvegardé : {filename}")

    def load_project(self):
        """Chargement d'un projet JSON"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filename: return

        with open(filename, 'r') as f:
            data = json.load(f)

        self.model.clear()
        self.view.clear_canvas()

        # Chargement Places
        for p in data["places"]:
            # p["tokens"] est une liste
            self.model.add_place(p["name"], p["tokens"])
            self.view.draw_place_visual(p["x"], p["y"], p["name"], p["tokens"])

        # Chargement Transitions
        for t in data["transitions"]:
            self.model.add_transition(t["name"])
            self.view.draw_transition_visual(t["x"], t["y"], t["name"])

        # Chargement Arcs
        for a in data["arcs"]:
            # On récupère "expression" (nouveau format) ou "weight" (ancien format fallback)
            expr = a.get("expression", a.get("weight", "x"))
            self.model.add_arc(a["source"], a["target"], expr)
            self.view.draw_arc_visual(a["source"], a["target"], expr)