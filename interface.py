# interface.py
import tkinter as tk
from model import PetriNet
from editor import PetriEditor

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Réseau de Petri")
        self.petri_net = PetriNet()
        self.editor = PetriEditor(self.petri_net, self)

        # Données graphiques
        self.canvas_item_to_name = {}
        self.name_to_coords = {}
        self.place_name_to_text_id = {}
        self.name_to_ids = {}

        # GUI
        self.toolbar = tk.Frame(root, bg="#ddd")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Boutons avec couleurs
        self.create_button("Place", "PLACE")        
        self.create_button("Transition", "TRANSITION")
        self.create_button("Arc", "ARC")              
        self.create_button("DEPLACER", "MOVE", bg="#aaccff")         # Bleu
        self.create_button("TIRER", "FIRE", bg="#ff9966")            # Orange
        self.create_button("SUPPRIMER", "DELETE", bg="#ff6666")      # Rouge

        self.lbl_mode = tk.Label(self.toolbar, text="Mode: PLACE", fg="blue")
        self.lbl_mode.pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    # Méthode create_button avec bg
    def create_button(self, text, mode, bg="SystemButtonFace"):
        tk.Button(self.toolbar, text=text, bg=bg,
                  command=lambda: self.editor.set_mode(mode)).pack(side=tk.LEFT)

    def update_mode_label(self, text):
        self.lbl_mode.config(text=text)

    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_name = self.canvas_item_to_name.get(item[0]) if item else None
        self.editor.handle_click(event.x, event.y, item_name)

    def on_canvas_drag(self, event):
        self.editor.handle_drag(event.x, event.y)

    def on_canvas_release(self, event):
        self.editor.handle_release()

    # Dessin places / transitions
    def draw_place_visual(self, x, y, name, tokens):
        r = 20
        sid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", width=2)
        tid = self.canvas.create_text(x, y, text=f"{name}\n({tokens})")
        self.register_object(name, x, y, [sid, tid], is_place=True)
        self.draw_tokens(x, y, tokens)

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 20
        sid = self.canvas.create_rectangle(x-w, y-h, x+w, y+h, fill="black")
        tid = self.canvas.create_text(x, y-h-15, text=name)
        self.register_object(name, x, y, [sid, tid], is_place=False)

    # Jetons rouges
    def draw_tokens(self, x, y, tokens):
        r_token = 5
        for i in range(tokens):
            token_x = x - tokens*6/2 + i*6
            token_y = y
            self.canvas.create_oval(token_x-r_token, token_y-r_token,
                                    token_x+r_token, token_y+r_token,
                                    fill="red", tags="TOKEN")

    # Enregistrement objets
    def register_object(self, name, x, y, ids, is_place):
        for i in ids:
            self.canvas_item_to_name[i] = name
        self.name_to_ids[name] = ids
        self.name_to_coords[name] = (x, y)
        if is_place:
            self.place_name_to_text_id[name] = ids[1]

    # Arcs
    def draw_arc_visual(self, source, target):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2, tags="ARC")

    # Mise à jour jetons
    def refresh_tokens(self):
        self.canvas.delete("TOKEN")
        for name, place in self.petri_net.places.items():
            txt_id = self.place_name_to_text_id.get(name)
            if txt_id:
                self.canvas.itemconfigure(txt_id, text=f"{name}\n({place.tokens})")
            x, y = self.name_to_coords[name]
            self.draw_tokens(x, y, place.tokens)

    # Déplacement
    def move_object(self, name, new_x, new_y):
        self.name_to_coords[name] = (new_x, new_y)
        ids = self.name_to_ids.get(name)
        if not ids: return
        if name.startswith("P"):
            r = 20
            self.canvas.coords(ids[0], new_x-r, new_y-r, new_x+r, new_y+r)
            self.canvas.coords(ids[1], new_x, new_y)
        elif name.startswith("T"):
            w, h = 15, 20
            self.canvas.coords(ids[0], new_x-w, new_y-h, new_x+w, new_y+h)
            self.canvas.coords(ids[1], new_x, new_y-h-15)
        self.redraw_arrows()
        self.refresh_tokens()

    def redraw_arrows(self):
        self.canvas.delete("ARC")
        for arc in self.petri_net.arcs:
            self.draw_arc_visual(arc.source.name, arc.target.name)

    # Suppression
    def delete_object(self, name):
        ids = self.name_to_ids.get(name, [])
        for i in ids:
            self.canvas.delete(i)
            self.canvas_item_to_name.pop(i, None)
        self.name_to_coords.pop(name, None)
        self.name_to_ids.pop(name, None)
        self.place_name_to_text_id.pop(name, None)
        self.petri_net.places.pop(name, None)
        self.petri_net.transitions.pop(name, None)
        self.petri_net.arcs = [a for a in self.petri_net.arcs
                               if a.source.name != name and a.target.name != name]
        self.redraw_arrows()
        self.refresh_tokens()


if __name__ == "__main__":
    root = tk.Tk()
    app = PetriApp(root)
    root.mainloop()
