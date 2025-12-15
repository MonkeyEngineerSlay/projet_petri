# editor.py
class PetriEditor:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = "PLACE"
        self.selected_source = None
        self.drag_item_name = None  # Pour déplacer

    def set_mode(self, mode):
        self.mode = mode
        self.selected_source = None
        self.drag_item_name = None
        info = f"Mode: {mode}"
        if mode == "MOVE":
            info = "Mode: DÉPLACEMENT (Glissez-déposez les objets)"
        elif mode == "DELETE":
            info = "Mode: SUPPRESSION (Clique sur un élément)"
        self.view.update_mode_label(info)

    def handle_click(self, x, y, item_name):
        """Clic sur le canvas"""
        if self.mode == "PLACE":
            name = f"P{len(self.model.places)}"
            self.model.add_place(name, 1)
            self.view.draw_place_visual(x, y, name, 1)

        elif self.mode == "TRANSITION":
            name = f"T{len(self.model.transitions)}"
            self.model.add_transition(name)
            self.view.draw_transition_visual(x, y, name)

        elif self.mode == "ARC":
            if not item_name: return
            if self.selected_source is None:
                self.selected_source = item_name
                self.view.update_mode_label(f"ARC: de {item_name} vers... ?")
            else:
                self.model.add_arc(self.selected_source, item_name)
                self.view.draw_arc_visual(self.selected_source, item_name)
                self.selected_source = None
                self.view.update_mode_label("ARC (Source ?)")

        elif self.mode == "FIRE":
            if item_name and item_name.startswith("T"):
                if self.model.fire(item_name):
                    self.view.refresh_tokens()

        elif self.mode == "MOVE":
            if item_name:
                self.drag_item_name = item_name

        elif self.mode == "DELETE":
            if item_name:
                self.view.delete_object(item_name)

    def handle_drag(self, x, y):
        if self.mode == "MOVE" and self.drag_item_name:
            self.view.move_object(self.drag_item_name, x, y)

    def handle_release(self):
        if self.mode == "MOVE":
            self.drag_item_name = None
