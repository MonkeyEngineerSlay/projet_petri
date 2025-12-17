# editor.py
import json
import tkinter.filedialog as filedialog
from analysis import PetriAnalyzer # <--- Import important !
import traceback # Pour afficher les détails de l'erreur dans la console

class PetriEditor:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = "PLACE"
        self.selected_source = None
        self.drag_item_name = None

    def set_mode(self, mode):
        # Actions immédiates
        if mode == "SAVE":
            self.save_project()
            return
        elif mode == "LOAD":
            self.load_project()
            return
        elif mode == "ANALYZE":
            self.run_analysis()
            return

        # Changement de mode normal
        self.mode = mode
        self.selected_source = None
        self.drag_item_name = None
        
        info = f"Mode: {mode}"
        if mode == "MOVE": info = "GLISSER-DÉPOSER"
        elif mode == "DELETE": info = "CLIQUEZ POUR SUPPRIMER"
        elif mode == "ARC": info = "SÉLECTIONNEZ LA SOURCE..."
        elif mode == "FIRE": info = "CLIQUEZ POUR TIRER UNE TRANSITION"
        
        self.view.update_mode_label(info)

    def run_analysis(self):
        """Lance l'analyse mathématique et affiche le résultat"""
        analyzer = PetriAnalyzer(self.model)
        
        try:
            # Calcul du graphe d'états
            props = analyzer.analyze_properties()
            
            # Formatage du message
            msg = f"--- RÉSULTATS DE L'ANALYSE ---\n\n"
            msg += f"Nombre d'états accessibles : {props.get('state_count', 0)}\n"
            msg += f"Nombre max de jetons observés : {props.get('max_tokens_seen', 0)}\n"
            
            # --- CORRECTION DE L'ERREUR ---
            # On vérifie si la clé est 'is_bounded' OU 'bounded' pour être compatible
            is_bounded = props.get('is_bounded') or props.get('bounded')
            
            if is_bounded:
                msg += "Le réseau est borné (Bounded).\n\n"
            
            if len(props.get('deadlocks', [])) == 0:
                msg += "✅ Aucun blocage (Deadlock) détecté.\n"
                msg += "Le réseau est vivant."
            else:
                msg += f"⚠️ ATTENTION : {len(props['deadlocks'])} blocage(s) détecté(s) !\n"
                if len(props['deadlocks']) > 0:
                    msg += f"Exemple d'état bloquant : {props['deadlocks'][0]}"

            self.view.show_analysis_results("Rapport d'Analyse", msg)
            
        except Exception as e:
            print(f"Erreur analyse : {e}")
            traceback.print_exc() # Affiche l'erreur exacte dans le terminal pour debug
            self.view.show_analysis_results("Erreur", f"L'analyse a échoué : {e}")

    def save_project(self):
        """Export JSON"""
        data = {"places": [], "transitions": [], "arcs": []}
        
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
            try:
                with open(filename, 'w') as f: json.dump(data, f, indent=4)
                self.view.update_mode_label(f"Sauvegardé : {filename}")
            except Exception as e:
                self.view.update_mode_label(f"Erreur : {e}")

    def load_project(self):
        """Import JSON"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filename: return

        try:
            with open(filename, 'r') as f: data = json.load(f)
            
            self.model.clear()
            self.view.clear_canvas()

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

            self.view.update_mode_label(f"Chargé : {filename}")
        except Exception as e:
            print(f"Erreur Load: {e}")
            self.view.update_mode_label("Erreur fichier corrompu")

    def handle_click(self, x, y, item_name):
        """Gestion des clics"""
        if self.mode == "PLACE":
            tokens = self.view.ask_token_number()
            if tokens is None: return 
            name = f"P{len(self.model.places)}"
            while name in self.model.places: name += "_"
            self.model.add_place(name, tokens)
            self.view.draw_place_visual(x, y, name, tokens)

        elif self.mode == "TRANSITION":
            name = f"T{len(self.model.transitions)}"
            while name in self.model.transitions: name += "_"
            self.model.add_transition(name)
            self.view.draw_transition_visual(x, y, name)

        elif self.mode == "ARC":
            if not item_name: return 
            if self.selected_source is None:
                self.selected_source = item_name
                self.view.update_mode_label(f"De {item_name} vers... ?")
            else:
                weight = self.view.ask_weight_number()
                if weight is None:
                    self.selected_source = None
                    self.view.update_mode_label("Annulé.")
                    return
                if self.model.add_arc(self.selected_source, item_name, weight):
                    self.view.draw_arc_visual(self.selected_source, item_name, weight)
                else:
                    self.view.update_mode_label("Connexion impossible")
                self.selected_source = None

        elif self.mode == "FIRE":
            if item_name and item_name.startswith("T"):
                if self.model.fire(item_name):
                    self.view.refresh_tokens()
                    self.view.update_mode_label(f"{item_name} FRANCHIE !")
                else:
                    self.view.update_mode_label(f"{item_name} BLOQUÉE")
        
        elif self.mode == "MOVE":
            if item_name: self.drag_item_name = item_name

        elif self.mode == "DELETE":
            if item_name:
                if self.model.remove_node(item_name):
                    self.view.delete_visual(item_name)
                    self.view.update_mode_label(f"{item_name} supprimé.")

    def handle_drag(self, x, y):
        if self.mode == "MOVE" and self.drag_item_name:
            self.view.move_object(self.drag_item_name, x, y)

    def handle_release(self):
        if self.mode == "MOVE":
            self.drag_item_name = None