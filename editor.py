import json
import tkinter.filedialog as filedialog

class PetriEditor:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = "PLACE"
        self.selected_source = None
        
        # Variables pour le déplacement
        self.drag_item_name = None  # Nom de l'objet en cours de déplacement

    def set_mode(self, mode):
        self.mode = mode
        self.selected_source = None
        self.drag_item_name = None
        
        info = f"Mode: {mode}"
        if mode == "MOVE":
            info = "Mode: DÉPLACEMENT (Glissez-déposez les objets)"

        elif mode == "REACH":
            #info = "Mode: REACHABILITY (clique sur le canvas)"
            self.view.show_reachability_graph()
            return

        elif mode == "SAVE":
            self.save_project()
            return
        elif mode == "LOAD":
            self.load_project()
            return
        self.mode = mode
        
        self.view.update_mode_label(info)

    def handle_click(self, x, y, item_name):
        """Clic simple (Button-1)"""
        if self.mode == "PLACE":

            tokens = self.view.ask_token_number()
            if tokens is None: return
            name = f"P{len(self.model.places)}"
            self.model.add_place(name, tokens)
            self.view.draw_place_visual(x, y, name, tokens)

        elif self.mode == "TRANSITION":
            name = f"T{len(self.model.transitions)}"
            self.model.add_transition(name)
            self.view.draw_transition_visual(x, y, name)

        elif self.mode == "ARC":
            if not item_name: return
            if self.selected_source is None:
                self.selected_source = item_name
                self.view.update_mode_label(f"ARC: de {item_name} vers... ?")
                return

            source = self.selected_source
            target = item_name

            weight = self.view.ask_weight_number()
            if weight is None:
                self.selected_source = None
                self.view.update_mode_label("ARC (Source ?)")
                return  # Annulation

            # créer l'arc avec le poids choisi
            self.model.add_arc(source, target, weight)
            self.view.draw_arc_visual(source, target)  # si tu veux afficher le poids, il faudra l’ajouter ici

            # reset de l’état
            self.selected_source = None
            self.view.update_mode_label("ARC (Source ?)")

            """else:
                self.model.add_arc(self.selected_source, item_name)
                self.view.draw_arc_visual(self.selected_source, item_name)
                self.selected_source = None
                self.view.update_mode_label("ARC (Source ?)")"""

        elif self.mode == "FIRE":
            if item_name and item_name.startswith("T"):
                if self.model.fire(item_name):
                    self.view.refresh_tokens()
        
        elif self.mode == "MOVE":
            # Début du déplacement : on mémorise ce qu'on a attrapé
            if item_name:
                self.drag_item_name = item_name

        elif self.mode == "REACH":
            # 1) construire le graphe d’états
            self.model.build_reachability_graph()
            # 2) générer une chaîne texte
            text = self.model.get_reachability_as_strings()
            # 3) demander à la vue de l’afficher
            self.view.show_text_window("Graphe de reachability", text)
            return

        elif self.mode == "DELETE":
            # --- AJOUT LOGIQUE SUPPRESSION ---
            if item_name:
                if self.model.remove_node(item_name):
                    self.view.delete_visual(item_name)


    def handle_drag(self, x, y):
        """Appelé quand la souris bouge avec le bouton enfoncé"""
        if self.mode == "MOVE" and self.drag_item_name:
            # On dit à la vue de déplacer visuellement l'objet
            self.view.move_object(self.drag_item_name, x, y)

    def handle_release(self):
        """Appelé quand on relâche le bouton de la souris"""
        if self.mode == "MOVE":
            self.drag_item_name = None # On lâche l'objet

    def save_project(self):
        data = {"places": [], "transitions": [], "arcs": []}

        # Adaptation nécessaire : Vérifie que 'self.view.name_to_coords' existe chez tes amis
        for name, place in self.model.places.items():
            x, y = self.view.name_to_coords.get(name, (0, 0))
            data["places"].append({"name": name, "tokens": place.tokens, "x": x, "y": y})

        for name, trans in self.model.transitions.items():
            x, y = self.view.name_to_coords.get(name, (0, 0))
            data["transitions"].append({"name": name, "x": x, "y": y})

        for arc in self.model.arcs:
            data["arcs"].append({"source": arc.source.name, "target": arc.target.name, "weight": arc.weight})

        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            with open(filename, 'w') as f: json.dump(data, f, indent=4)
            print(f"Sauvegardé : {filename}")

    def load_project(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filename: return

        with open(filename, 'r') as f:
            data = json.load(f)

        self.model.clear()  # Appelle la fonction qu'on a ajoutée dans model.py
        self.view.clear_canvas()  # Appelle la fonction qu'on a ajoutée dans interface.py

        for p in data["places"]:
            self.model.add_place(p["name"], p["tokens"])
            self.view.draw_place_visual(p["x"], p["y"], p["name"], p["tokens"])

        for t in data["transitions"]:
            self.model.add_transition(t["name"])
            self.view.draw_transition_visual(t["x"], t["y"], t["name"])

        for a in data["arcs"]:
            w = a.get("weight", 1)
            self.model.add_arc(a["source"], a["target"], w)
            self.view.draw_arc_visual(a["source"], a["target"], w)



