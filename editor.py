class PetriEditor:
    def __init__(self, model, view):
        self.model = model       # Le modèle mathématique
        self.view = view         # L'interface graphique
        self.mode = "PLACE"      # Mode par défaut
        self.selected_source = None
        self.drag_item_name = None

    def set_mode(self, mode):
        self.mode = mode
        self.selected_source = None
        self.drag_item_name = None
        
        # Mise à jour du texte d'info dans l'interface
        info = f"Mode: {mode}"
        if mode == "MOVE": info = "GLISSER-DÉPOSER (Maintenez le clic)"
        elif mode == "ARC": info = "SÉLECTIONNEZ LA SOURCE..."
        elif mode == "FIRE": info = "MODE TIR (Cliquez sur une transition)"
        
        self.view.update_mode_label(info)

    def handle_click(self, x, y, item_name):
        """Gère le clic selon le mode actuel"""
        
        # 1. Mode PLACE : Créer un rond AVEC choix des jetons
        if self.mode == "PLACE":
            # On demande le nombre de jetons via la Vue
            tokens = self.view.ask_token_number()
            
            # Si l'utilisateur annule (Croix ou Annuler), on arrête
            if tokens is None: return 

            name = f"P{len(self.model.places)}"
            self.model.add_place(name, tokens)
            self.view.draw_place_visual(x, y, name, tokens)

        # 2. Mode TRANSITION : Créer un carré
        elif self.mode == "TRANSITION":
            name = f"T{len(self.model.transitions)}"
            self.model.add_transition(name)
            self.view.draw_transition_visual(x, y, name)

        # 3. Mode ARC : Relier deux objets AVEC choix du poids
        elif self.mode == "ARC":
            if not item_name: return # Clic dans le vide
            
            if self.selected_source is None:
                # Premier clic : Source
                self.selected_source = item_name
                self.view.update_mode_label(f"De {item_name} vers... ?")
            else:
                # Deuxième clic : Cible
                # On demande le poids via la Vue
                weight = self.view.ask_weight_number()
                
                # Si l'utilisateur annule
                if weight is None:
                    self.selected_source = None
                    self.view.update_mode_label("Annulé. (Source ?)")
                    return

                # Création logique + Visuelle
                self.model.add_arc(self.selected_source, item_name, weight)
                self.view.draw_arc_visual(self.selected_source, item_name, weight)
                
                # Reset pour le prochain arc
                self.selected_source = None
                self.view.update_mode_label("Nouvel Arc (Source ?)")

        # 4. Mode FIRE : Tirer une transition
        elif self.mode == "FIRE":
            if item_name and item_name.startswith("T"):
                if self.model.fire(item_name):
                    self.view.refresh_tokens()
                    self.view.update_mode_label(f"{item_name} FRANCHIE !")
                else:
                    self.view.update_mode_label(f"{item_name} BLOQUÉE (Manque jetons)")
        
        # 5. Mode MOVE : Attraper un objet
        elif self.mode == "MOVE":
            if item_name:
                self.drag_item_name = item_name

    def handle_drag(self, x, y):
        """Gère le mouvement de la souris (pour le déplacement)"""
        if self.mode == "MOVE" and self.drag_item_name:
            self.view.move_object(self.drag_item_name, x, y)

    def handle_release(self):
        """Gère le relâchement de la souris"""
        if self.mode == "MOVE":
            self.drag_item_name = None