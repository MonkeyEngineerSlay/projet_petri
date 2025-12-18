import tkinter as tk
from tkinter import simpledialog
from petri_model import PetriNet
from editor import PetriEditor


class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MVC Petri Editor - Avec Déplacement")

        self.petri_net = PetriNet()
        self.editor = PetriEditor(self.petri_net, self)

        # Données graphiques
        self.canvas_item_to_name = {}
        self.name_to_coords = {}
        self.place_name_to_text_id = {}
        self.name_to_ids = {}

        # --- STYLE UNIQUE ---
        self.STYLE = {
            "bg_toolbar": "#2c3e50",
            "btn_bg": "#34495e",
            "btn_fg": "white",
            "btn_active": "#1abc9c",
            "fire_bg": "#e67e22",
        }

        # Toolbar unique
        self.toolbar = tk.Frame(root, bg=self.STYLE["bg_toolbar"], height=50, pady=10)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Boutons (tous via create_styled_btn)
        self.create_styled_btn("Place", "PLACE")
        self.create_styled_btn("Transition", "TRANSITION")
        self.create_styled_btn("Arc", "ARC")
        self.create_styled_btn("Tirer", "FIRE", bg_color=self.STYLE["fire_bg"])
        self.create_styled_btn("Déplacer", "MOVE", bg_color="#f39c12")
        self.create_styled_btn("Supprimer", "DELETE", bg_color="#c0392b")
        self.create_styled_btn("Reachability", "REACH", bg_color="#8e44ad")
        self.create_styled_btn("Sauver", "SAVE", bg_color="#27ae60")
        self.create_styled_btn("Charger", "LOAD", bg_color="#16a085")

        # Label de mode
        self.lbl_mode = tk.Label(self.toolbar, text="Mode: PLACE",
                                 fg="white", bg=self.STYLE["bg_toolbar"])
        self.lbl_mode.pack(side=tk.RIGHT, padx=20)

        # Canvas
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    # ---------- BOUTONS ----------

    def create_styled_btn(self, text, mode, bg_color=None):
        if bg_color is None:
            bg_color = self.STYLE["btn_bg"]
        btn = tk.Button(
            self.toolbar,
            text=text,
            bg=bg_color,
            fg=self.STYLE["btn_fg"],
            relief="flat",
            activebackground=self.STYLE["btn_active"],
            padx=10, pady=5, borderwidth=0,
            command=lambda: self.editor.set_mode(mode)
        )
        btn.pack(side=tk.LEFT, padx=3)

    # Gardée pour compatibilité éventuelle (si utilisée ailleurs)
    def create_button(self, text, mode, bg="SystemButtonFace"):
        tk.Button(self.toolbar, text=text, bg=bg,
                  command=lambda: self.editor.set_mode(mode)).pack(side=tk.LEFT)

    def update_mode_label(self, text):
        self.lbl_mode.config(text=text)

    # ---------- ÉVÉNEMENTS SOURIS ----------

    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_name = self.canvas_item_to_name.get(item[0]) if item else None
        self.editor.handle_click(event.x, event.y, item_name)

    def on_canvas_drag(self, event):
        self.editor.handle_drag(event.x, event.y)

    def on_canvas_release(self, event):
        self.editor.handle_release()

    # ---------- DESSIN ----------

    def draw_place_visual(self, x, y, name, tokens):
        r = 20
        sid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", width=2)
        tid = self.canvas.create_text(x, y, text=f"{name}\n({tokens})")
        self.register_object(name, x, y, [sid, tid], is_place=True)

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 20
        sid = self.canvas.create_rectangle(x - w, y - h, x + w, y + h, fill="black")
        tid = self.canvas.create_text(x, y - h - 15, text=name)
        self.register_object(name, x, y, [sid, tid], is_place=False)

    def register_object(self, name, x, y, ids, is_place):
        for i in ids:
            self.canvas_item_to_name[i] = name
        self.name_to_ids[name] = ids
        self.name_to_coords[name] = (x, y)
        if is_place:
            self.place_name_to_text_id[name] = ids[1]

    def draw_arc_visual(self, source, target):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST,
                                width=2, tags="ARC")

    def refresh_tokens(self):
        for name, place in self.petri_net.places.items():
            txt_id = self.place_name_to_text_id.get(name)
            if txt_id:
                self.canvas.itemconfigure(txt_id,
                                          text=f"{name}\n({place.tokens})")

    def move_object(self, name, new_x, new_y):
        self.name_to_coords[name] = (new_x, new_y)
        ids = self.name_to_ids.get(name)
        if not ids:
            return
        if name.startswith("P"):
            r = 20
            self.canvas.coords(ids[0], new_x - r, new_y - r, new_x + r, new_y + r)
            self.canvas.coords(ids[1], new_x, new_y)
        elif name.startswith("T"):
            w, h = 15, 20
            self.canvas.coords(ids[0], new_x - w, new_y - h, new_x + w, new_y + h)
            self.canvas.coords(ids[1], new_x, new_y - h - 15)
        self.redraw_arrows()

    def redraw_arrows(self):
        self.canvas.delete("ARC")
        for arc in self.petri_net.arcs:
            self.draw_arc_visual(arc.source.name, arc.target.name)

    # ---------- REACHABILITY & POPUPS ----------

    def show_reachability(self):
        self.petri_net.build_reachability_graph()
        text = self.petri_net.get_reachability_as_strings()
        self.show_text_window("Graphe de reachability", text)

    def show_text_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        txt = tk.Text(win, width=80, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", text)

    def ask_token_number(self):
        return simpledialog.askinteger("Config", "Nombre de jetons :",
                                       initialvalue=0, minvalue=0)

    def ask_weight_number(self):
        return simpledialog.askinteger("Config", "Poids de l'arc :",
                                       initialvalue=1, minvalue=1)

    # ---------- GESTION VISUELLE ----------

    def delete_visual(self, name):
        ids = self.name_to_ids.get(name)
        if ids:
            for item_id in ids:
                self.canvas.delete(item_id)
            del self.name_to_ids[name]
            del self.name_to_coords[name]
            keys_to_remove = [k for k, v in self.canvas_item_to_name.items()
                              if v == name]
            for k in keys_to_remove:
                del self.canvas_item_to_name[k]
        self.redraw_arrows()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.canvas_item_to_name.clear()
        self.name_to_coords.clear()
        self.name_to_ids.clear()

    def show_reachability_graph(self):
        self.petri_net.build_reachability_graph()

        win = tk.Toplevel(self.root)
        win.title("Reachability graph")
        canvas = tk.Canvas(win, width=800, height=600, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        # 1) placer les états en cercle
        node_pos = {}
        n = len(self.petri_net.id_to_marking)
        R = 200
        cx, cy = 400, 300
        for idx, (node_id, marking) in enumerate(self.petri_net.id_to_marking.items()):
            angle = 2 * 3.14159 * idx / max(n, 1)
            x = cx + R * (0.8 * (1 if n == 1 else 1)) * (float(__import__("math").cos(angle)))
            y = cy + R * (float(__import__("math").sin(angle)))
            node_pos[node_id] = (x, y)
            r = 35
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ecf0f1")
            label = f"{node_id}: {marking}"
            canvas.create_text(x, y, text=label)

        # 2) tracer les arcs
        for src, dst, t_name in self.petri_net.edges:
            x1, y1 = node_pos[src]
            x2, y2 = node_pos[dst]
            canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            canvas.create_text(mx, my - 10, text=t_name, fill="blue")
