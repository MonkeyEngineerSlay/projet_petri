# interface.py
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox # <--- Important pour la popup résultats
from model import PetriNet
from editor import PetriEditor

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulateur Réseau de Petri - Complet")
        self.root.geometry("1000x700")
        
        # --- STYLE MODERNE ---
        self.STYLE = {
            "bg_app": "#f0f2f5",       "bg_toolbar": "#2c3e50",
            "btn_bg": "#34495e",       "btn_fg": "white",
            "btn_active": "#1abc9c",   "fire_bg": "#e74c3c",
            "canvas_bg": "white",      "place_fill": "#ecf0f1",
            "place_outline": "#2980b9","trans_fill": "#2c3e50",
            "font_ui": ("Segoe UI", 10, "bold"),
            "font_canvas": ("Consolas", 10, "bold"),
            "arc_color": "#7f8c8d",    "weight_color": "#c0392b",
            "analyze_btn": "#3498db"   # Bleu clair pour Analyser
        }
        self.root.configure(bg=self.STYLE["bg_app"])

        # Initialisation MVC
        self.petri_net = PetriNet()
        self.editor = PetriEditor(self.petri_net, self)
        
        # Dictionnaires de gestion graphique
        self.canvas_item_to_name = {}
        self.name_to_coords = {}
        self.place_name_to_text_id = {}
        self.name_to_ids = {} 

        # --- BARRE D'OUTILS ---
        self.toolbar = tk.Frame(root, bg=self.STYLE["bg_toolbar"], height=60, pady=10)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Groupe Création
        self.create_styled_btn("O Place", "PLACE")
        self.create_styled_btn("[] Transition", "TRANSITION")
        self.create_styled_btn("-> Arc", "ARC")
        
        # Séparateur
        tk.Frame(self.toolbar, width=20, bg=self.STYLE["bg_toolbar"]).pack(side=tk.LEFT)
        
        # Groupe Édition
        self.create_styled_btn("M Déplacer", "MOVE", bg_color="#f39c12")
        self.create_styled_btn("X Supprimer", "DELETE", bg_color="#c0392b")
        
        # Séparateur
        tk.Frame(self.toolbar, width=20, bg=self.STYLE["bg_toolbar"]).pack(side=tk.LEFT)
        
        # Groupe Fichier
        self.create_styled_btn("Sauver", "SAVE", bg_color="#27ae60")
        self.create_styled_btn("Charger", "LOAD", bg_color="#8e44ad")
        
        # Groupe Simulation & Analyse (à droite)
        tk.Frame(self.toolbar, width=20, bg=self.STYLE["bg_toolbar"]).pack(side=tk.LEFT)
        self.create_styled_btn("? Analyser", "ANALYZE", bg_color=self.STYLE["analyze_btn"]) # <--- BOUTON ANALYSER
        self.create_styled_btn("! TIRER !", "FIRE", bg_color=self.STYLE["fire_bg"])

        # Label d'information
        self.lbl_mode = tk.Label(self.toolbar, text="Mode: PLACE", 
                                 bg=self.STYLE["bg_toolbar"], fg="#ecf0f1", 
                                 font=("Segoe UI", 12, "bold"))
        self.lbl_mode.pack(side=tk.RIGHT, padx=20)

        # --- ZONE DE DESSIN ---
        self.canvas_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.STYLE["canvas_bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def create_styled_btn(self, text, mode, bg_color=None):
        if bg_color is None: bg_color = self.STYLE["btn_bg"]
        btn = tk.Button(self.toolbar, text=text, bg=bg_color, fg=self.STYLE["btn_fg"],
                        font=self.STYLE["font_ui"], relief="flat",
                        activebackground=self.STYLE["btn_active"], activeforeground="white",
                        padx=10, pady=5, borderwidth=0,
                        command=lambda: self.editor.set_mode(mode))
        btn.pack(side=tk.LEFT, padx=3)

    def update_mode_label(self, text):
        self.lbl_mode.config(text=text)

    # --- POPUPS ---
    def ask_token_number(self):
        return simpledialog.askinteger("Configuration", "Nombre de jetons initial :", initialvalue=0, minvalue=0)

    def ask_weight_number(self):
        return simpledialog.askinteger("Poids", "Poids de l'arc :", initialvalue=1, minvalue=1)

    def show_analysis_results(self, title, message):
        """Affiche une popup avec les résultats"""
        messagebox.showinfo(title, message)

    # --- GESTION VISUELLE ---
    def delete_visual(self, name):
        """Supprime un objet et nettoie les dictionnaires"""
        ids = self.name_to_ids.get(name)
        if ids:
            for item_id in ids:
                self.canvas.delete(item_id)
            del self.name_to_ids[name]
            del self.name_to_coords[name]
            if name in self.place_name_to_text_id:
                del self.place_name_to_text_id[name]
            # Nettoyage inverse
            keys_to_remove = [k for k, v in self.canvas_item_to_name.items() if v == name]
            for k in keys_to_remove:
                del self.canvas_item_to_name[k]
        self.redraw_arrows()

    def clear_canvas(self):
        """Tout effacer"""
        self.canvas.delete("all")
        self.canvas_item_to_name.clear()
        self.name_to_coords.clear()
        self.place_name_to_text_id.clear()
        self.name_to_ids.clear()

    # --- EVENTS (Vers l'éditeur) ---
    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_name = self.canvas_item_to_name.get(item[0]) if item else None
        self.editor.handle_click(event.x, event.y, item_name)

    def on_canvas_drag(self, event):
        self.editor.handle_drag(event.x, event.y)

    def on_canvas_release(self, event):
        self.editor.handle_release()

    # --- DESSIN PRIMITIF ---
    def draw_place_visual(self, x, y, name, tokens):
        r = 25
        sid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.STYLE["place_fill"], outline=self.STYLE["place_outline"], width=3)
        tid = self.canvas.create_text(x, y, text=f"{name}\n({tokens})", font=self.STYLE["font_canvas"], fill="#2c3e50")
        self.register_object(name, x, y, [sid, tid], is_place=True)

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 25
        sid = self.canvas.create_rectangle(x-w, y-h, x+w, y+h, fill=self.STYLE["trans_fill"], outline="")
        tid = self.canvas.create_text(x, y-h-20, text=name, font=self.STYLE["font_canvas"], fill="#2c3e50")
        self.register_object(name, x, y, [sid, tid], is_place=False)

    def register_object(self, name, x, y, ids, is_place):
        for i in ids: self.canvas_item_to_name[i] = name
        self.name_to_ids[name] = ids
        self.name_to_coords[name] = (x, y)
        if is_place: self.place_name_to_text_id[name] = ids[1]

    def draw_arc_visual(self, source, target, weight=1):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=3, fill=self.STYLE["arc_color"], tags="ARC")
        if weight > 1:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y - 10, text=str(weight), font=("Arial", 12, "bold"), fill=self.STYLE["weight_color"], tags="ARC")

    def refresh_tokens(self):
        for name, place in self.petri_net.places.items():
            txt_id = self.place_name_to_text_id.get(name)
            if txt_id: self.canvas.itemconfigure(txt_id, text=f"{name}\n({place.tokens})")

    def move_object(self, name, new_x, new_y):
        self.name_to_coords[name] = (new_x, new_y)
        ids = self.name_to_ids.get(name)
        if not ids: return
        
        if name.startswith("P"):
            r = 25
            self.canvas.coords(ids[0], new_x-r, new_y-r, new_x+r, new_y+r)
            self.canvas.coords(ids[1], new_x, new_y)
        elif name.startswith("T"):
            w, h = 15, 25
            self.canvas.coords(ids[0], new_x-w, new_y-h, new_x+w, new_y+h)
            self.canvas.coords(ids[1], new_x, new_y-h-20)
        self.redraw_arrows()

    def redraw_arrows(self):
        self.canvas.delete("ARC")
        for arc in self.petri_net.arcs:
            self.draw_arc_visual(arc.source.name, arc.target.name, arc.weight)