import tkinter as tk
import tkinter.simpledialog as simpledialog
from model import PetriNet
from editor import PetriEditor

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulateur Réseau de Petri")
        self.root.geometry("900x650")
        
        # --- CONFIGURATION DU STYLE (Couleurs & Polices) ---
        self.STYLE = {
            "bg_app": "#f0f2f5",       # Gris très clair (fond)
            "bg_toolbar": "#2c3e50",   # Bleu nuit (barre d'outils)
            "btn_bg": "#34495e",       # Bouton normal
            "btn_fg": "white",         # Texte bouton
            "btn_active": "#1abc9c",   # Bouton survolé (Turquoise)
            "fire_bg": "#e74c3c",      # Bouton TIRER (Rouge)
            "canvas_bg": "white",      # Fond zone de dessin
            "place_fill": "#ecf0f1",   # Intérieur Place
            "place_outline": "#2980b9",# Contour Place (Bleu)
            "trans_fill": "#2c3e50",   # Intérieur Transition
            "font_ui": ("Segoe UI", 10, "bold"),
            "font_canvas": ("Consolas", 10, "bold"),
            "arc_color": "#7f8c8d",    # Gris pour les flèches
            "weight_color": "#c0392b"  # Rouge pour le poids
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
        self.toolbar = tk.Frame(root, bg=self.STYLE["bg_toolbar"], height=50, pady=10)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Création des boutons stylisés
        self.create_styled_btn("O Place", "PLACE")
        self.create_styled_btn("[] Transition", "TRANSITION")
        self.create_styled_btn("-> Arc", "ARC")
        self.create_styled_btn("M Déplacer", "MOVE", bg_color="#f39c12")
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
        
        # Bindings (Événements souris)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def create_styled_btn(self, text, mode, bg_color=None):
        if bg_color is None:
            bg_color = self.STYLE["btn_bg"]
            
        btn = tk.Button(self.toolbar, text=text, 
                        bg=bg_color, fg=self.STYLE["btn_fg"],
                        font=self.STYLE["font_ui"], relief="flat",
                        activebackground=self.STYLE["btn_active"],
                        activeforeground="white",
                        padx=15, pady=5, borderwidth=0,
                        command=lambda: self.editor.set_mode(mode))
        btn.pack(side=tk.LEFT, padx=5)

    def update_mode_label(self, text):
        self.lbl_mode.config(text=text)

    # --- POPUPS (Demande d'infos) ---
    def ask_token_number(self):
        """Ouvre une fenêtre pour demander le nombre de jetons"""
        return simpledialog.askinteger("Configuration", "Nombre de jetons initial :", 
                                     initialvalue=0, minvalue=0)

    def ask_weight_number(self):
        """Ouvre une fenêtre pour demander le poids de l'arc"""
        return simpledialog.askinteger("Poids de l'arc", "Poids (Entier > 0) :", 
                                     initialvalue=1, minvalue=1)

    # --- GESTION ÉVÉNEMENTS (Passe-plat vers Editor) ---
    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_name = self.canvas_item_to_name.get(item[0]) if item else None
        self.editor.handle_click(event.x, event.y, item_name)

    def on_canvas_drag(self, event):
        self.editor.handle_drag(event.x, event.y)

    def on_canvas_release(self, event):
        self.editor.handle_release()

    # --- DESSIN ---
    def draw_place_visual(self, x, y, name, tokens):
        r = 25
        sid = self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                      fill=self.STYLE["place_fill"], 
                                      outline=self.STYLE["place_outline"], 
                                      width=3)
        tid = self.canvas.create_text(x, y, text=f"{name}\n({tokens})", 
                                      font=self.STYLE["font_canvas"], fill="#2c3e50")
        
        self.register_object(name, x, y, [sid, tid], is_place=True)

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 25
        sid = self.canvas.create_rectangle(x-w, y-h, x+w, y+h, 
                                           fill=self.STYLE["trans_fill"], outline="")
        tid = self.canvas.create_text(x, y-h-20, text=name, 
                                      font=self.STYLE["font_canvas"], fill="#2c3e50")
        
        self.register_object(name, x, y, [sid, tid], is_place=False)

    def register_object(self, name, x, y, ids, is_place):
        for i in ids:
            self.canvas_item_to_name[i] = name
        self.name_to_ids[name] = ids
        self.name_to_coords[name] = (x, y)
        if is_place:
            self.place_name_to_text_id[name] = ids[1]

    def draw_arc_visual(self, source, target, weight=1):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        
        # Dessin de la flèche
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=3, 
                                fill=self.STYLE["arc_color"], tags="ARC")
        
        # Si le poids > 1, on l'écrit en rouge au milieu
        if weight > 1:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y - 10, text=str(weight), 
                                    font=("Arial", 12, "bold"), 
                                    fill=self.STYLE["weight_color"], tags="ARC")

    def refresh_tokens(self):
        for name, place in self.petri_net.places.items():
            txt_id = self.place_name_to_text_id.get(name)
            if txt_id:
                self.canvas.itemconfigure(txt_id, text=f"{name}\n({place.tokens})")

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
            source_name = arc.source.name
            target_name = arc.target.name
            # On n'oublie pas de redessiner avec le bon poids !
            self.draw_arc_visual(source_name, target_name, arc.weight)