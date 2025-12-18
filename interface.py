#interface.py
import tkinter as tk
import math

from tkinter import simpledialog
from tkinter import ttk  # Nécessaire pour le menu déroulant (Combobox)
from model import PetriNet
from editor import PetriEditor

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MVC Petri Editor - CPN (Coloré & Visuel)")

        self.petri_net = PetriNet()
        self.editor = PetriEditor(self.petri_net, self)

        # Données graphiques
        self.canvas_item_to_name = {}    # ID Canvas -> Nom Objet (P1, T1...)
        self.name_to_coords = {}         # Nom Objet -> (x, y)
        self.place_name_to_text_id = {}  # Nom Place -> ID du texte (pour mise à jour)
        self.name_to_ids = {}            # Nom Objet -> Liste [ID_Forme, ID_Texte, ...]

        # --- STYLE UNIQUE ---
        self.STYLE = {
            "bg_toolbar": "#2c3e50",
            "btn_bg": "#34495e",
            "btn_fg": "white",
            "btn_active": "#1abc9c",
            "fire_bg": "#e67e22",
        }

        # Toolbar
        self.toolbar = tk.Frame(root, bg=self.STYLE["bg_toolbar"], height=50, pady=10)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Création des boutons
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
                                 fg="white", bg=self.STYLE["bg_toolbar"], font=("Arial", 10, "bold"))
        self.lbl_mode.pack(side=tk.RIGHT, padx=20)

        # Canvas
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings (Événements souris)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    # ---------- BOUTONS & BARRE D'OUTILS ----------

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

    # ---------- GESTION DES COULEURS ----------

    def get_token_color(self, token_value):
        """Convertit la valeur du jeton (texte) en code couleur hexadécimal."""
        val = str(token_value).lower().strip()
        
        # Palette de couleurs CPN
        colors = {
            "rouge": "#e74c3c", "red": "#e74c3c",
            "vert": "#2ecc71", "green": "#2ecc71",
            "bleu": "#3498db", "blue": "#3498db",
            "jaune": "#f1c40f", "yellow": "#f1c40f",
            "noir": "#2c3e50", "black": "#2c3e50",
            "orange": "#e67e22",
            "violet": "#9b59b6", "purple": "#9b59b6"
        }
        # Retourne la couleur correspondante ou Gris foncé par défaut
        return colors.get(val, "#2c3e50")

    # ---------- DESSIN (Visuel Amélioré) ----------

    def draw_place_visual(self, x, y, name, tokens):
        r = 25
        # Dessin du cercle de la Place
        sid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", width=2, outline="#2c3e50")
        
        # Le nom est affiché SOUS la place pour ne pas gêner les billes
        tid = self.canvas.create_text(x, y + 35, text=name, font=("Arial", 9, "bold"), fill="#2c3e50")
        
        self.register_object(name, x, y, [sid, tid], is_place=True)
        
        # Appel de la fonction qui dessine les billes à l'intérieur
        self.draw_tokens_inside(name, x, y, tokens)

    def draw_tokens_inside(self, name, x, y, tokens):
        """Dessine des petits cercles colorés pour chaque jeton à l'intérieur de la place."""
        # 1. Nettoyer les anciens jetons visuels de cette place
        self.canvas.delete(f"TOKEN_{name}")
        
        if not tokens: return

        # Si trop de jetons, on affiche juste un nombre pour éviter la saturation
        if len(tokens) > 5:
            self.canvas.create_text(x, y, text=str(len(tokens)), tags=f"TOKEN_{name}", font=("Arial", 12, "bold"))
            return

        # 2. Dessiner chaque jeton avec un léger décalage
        offsets = [(-10, -10), (10, -10), (-10, 10), (10, 10), (0, 0)]
        
        for i, token_val in enumerate(tokens):
            # Calcul de la position
            dx, dy = offsets[i] if i < len(offsets) else (0,0)
            tx, ty = x + dx, y + dy
            
            # Récupération de la couleur
            color = self.get_token_color(token_val)
            
            # Dessin de la bille (rayon 6)
            self.canvas.create_oval(tx - 6, ty - 6, tx + 6, ty + 6, 
                                    fill=color, outline="white", width=1, 
                                    tags=f"TOKEN_{name}")

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 20
        sid = self.canvas.create_rectangle(x - w, y - h, x + w, y + h, fill="black")
        tid = self.canvas.create_text(x, y - h - 15, text=name, font=("Arial", 10, "bold"))
        self.register_object(name, x, y, [sid, tid], is_place=False)

    def register_object(self, name, x, y, ids, is_place):
        for i in ids:
            self.canvas_item_to_name[i] = name
        self.name_to_ids[name] = ids
        self.name_to_coords[name] = (x, y)
        if is_place:
            self.place_name_to_text_id[name] = ids[1]

    def draw_arc_visual(self, source, target, label="x"):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        
        # Arc
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2, tags="ARC", fill="#34495e")
        
        # Label (Variable)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        self.canvas.create_text(xm, ym - 10, text=str(label), fill="#e74c3c", font=("Arial", 10, "bold"), tags="ARC")

    def refresh_tokens(self):
        """Met à jour l'affichage graphique des jetons après un tir."""
        for name, place in self.petri_net.places.items():
            if name in self.name_to_coords:
                x, y = self.name_to_coords[name]
                # On redessine les billes avec le nouvel état
                self.draw_tokens_inside(name, x, y, place.tokens)

    def move_object(self, name, new_x, new_y):
        self.name_to_coords[name] = (new_x, new_y)
        ids = self.name_to_ids.get(name)
        if not ids: return

        if name.startswith("P"):
            r = 25
            self.canvas.coords(ids[0], new_x - r, new_y - r, new_x + r, new_y + r)
            self.canvas.coords(ids[1], new_x, new_y + 35)
            
            # DÉPLACEMENT : On redessine les jetons à la nouvelle position
            place = self.petri_net.places.get(name)
            if place:
                self.draw_tokens_inside(name, new_x, new_y, place.tokens)
                
        elif name.startswith("T"):
            w, h = 15, 20
            self.canvas.coords(ids[0], new_x - w, new_y - h, new_x + w, new_y + h)
            self.canvas.coords(ids[1], new_x, new_y - h - 15)
        
        self.redraw_arrows()

    def redraw_arrows(self):
        self.canvas.delete("ARC")
        for arc in self.petri_net.arcs:
            self.draw_arc_visual(arc.source.name, arc.target.name, arc.expression)

    # ---------- DIALOGUES (Fenêtres de saisie) ----------

    def ask_token_builder(self):
        """
        Ouvre une fenêtre complexe pour composer un multiensemble de jetons colorés.
        Retourne une liste, par exemple : ["Rouge", "Rouge", "Bleu"]
        """
        # Création de la fenêtre popup
        popup = tk.Toplevel(self.root)
        popup.title("Constructeur de Jetons")
        popup.geometry("300x250")
        
        # Variables pour stocker les choix
        selected_color = tk.StringVar(value="Rouge")
        selected_qty = tk.IntVar(value=1)
        final_tokens = [] # La liste qu'on va retourner
        
        # Zone de choix
        frame_input = tk.Frame(popup, pady=10)
        frame_input.pack()
        
        tk.Label(frame_input, text="Couleur :").grid(row=0, column=0)
        colors = ["Rouge", "Bleu", "Vert", "Jaune", "Noir", "Orange", "Violet"]
        
        # Menu déroulant (Combobox)
        cb_color = ttk.Combobox(frame_input, textvariable=selected_color, values=colors, state="readonly", width=10)
        cb_color.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_input, text="Qté :").grid(row=1, column=0)
        sp_qty = tk.Spinbox(frame_input, from_=1, to=100, textvariable=selected_qty, width=5)
        sp_qty.grid(row=1, column=1, padx=5)
        
        # Liste d'affichage (pour voir ce qu'on a ajouté)
        list_display = tk.Listbox(popup, height=6, width=40)
        list_display.pack(padx=10, pady=5)
        
        # Fonction locale pour ajouter à la liste
        def add_tokens():
            color = selected_color.get()
            qty = selected_qty.get()
            # Ajout visuel
            list_display.insert(tk.END, f"{qty} x {color}")
            # Ajout logique
            for _ in range(qty):
                final_tokens.append(color)
        
        btn_add = tk.Button(frame_input, text="Ajouter", command=add_tokens, bg="#ecf0f1")
        btn_add.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Bouton de validation finale
        def validate():
            popup.destroy() # Ferme la fenêtre et rend la main au programme
            
        btn_ok = tk.Button(popup, text="Valider la création", command=validate, bg="#2ecc71", fg="white")
        btn_ok.pack(pady=10, fill=tk.X, padx=20)
        
        # On attend que la fenêtre soit fermée
        self.root.wait_window(popup)
        
        # Retourne la liste (ou None si vide/annulé)
        return final_tokens if final_tokens else None

    # Gardé pour compatibilité ou fallback
    def ask_token_string(self):
        return simpledialog.askstring("Config", "Jetons (ex: 1, 2, A)", initialvalue="1")

    def ask_arc_variable(self):
        return simpledialog.askstring("Config CPN", "Variable d'arc (ex: x, y) :", initialvalue="x")

    def show_text_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        txt = tk.Text(win, width=80, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", text)

    # ---------- NETTOYAGE ----------

    def delete_visual(self, name):
        ids = self.name_to_ids.get(name)
        if ids:
            for item_id in ids:
                self.canvas.delete(item_id)
            # Supprime aussi les jetons visuels associés
            self.canvas.delete(f"TOKEN_{name}")
            
            del self.name_to_ids[name]
            del self.name_to_coords[name]
            keys_to_remove = [k for k, v in self.canvas_item_to_name.items() if v == name]
            for k in keys_to_remove:
                del self.canvas_item_to_name[k]
            if name in self.place_name_to_text_id:
                del self.place_name_to_text_id[name]
        self.redraw_arrows()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.canvas_item_to_name.clear()
        self.name_to_coords.clear()
        self.name_to_ids.clear()
        self.place_name_to_text_id.clear()

    def show_reachability(self):
        self.petri_net.build_reachability_graph()  # ← APPEL MODEL
        text = self.petri_net.get_reachability_as_strings()
        self.show_text_window("Graphe de reachability", text)

    def show_reachability_graph(self):
        self.petri_net.build_reachability_graph()  # ← 1

        win = tk.Toplevel(self.root)
        win.title("Reachability graph")
        canvas = tk.Canvas(win, width=800, height=600, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        # Placement noeuds
        node_pos = {}
        n = len(self.petri_net.id_to_marking)  # ← SI n=1 → 1 seul nœud !
        R = 200
        cx, cy = 400, 300
        for idx, (node_id, marking) in enumerate(self.petri_net.id_to_marking.items()):
            angle = 2 * 3.14159 * idx / max(n, 1)
            x = cx + R * (0.8 * (1 if n == 1 else 1)) * (float(math.cos(angle)))
            y = cy + R * (float(math.sin(angle)))
            node_pos[node_id] = (x, y)
            r = 35
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ecf0f1")
            label = f"{node_id}: {marking}"
            canvas.create_text(x, y, text=label)

        # Arcs (disparaissent si edges vide)
        for src, dst, t_name in self.petri_net.edges:  # ← SI edges=[] → AUCUN ARC !
            x1, y1 = node_pos[src]
            x2, y2 = node_pos[dst]
            canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            canvas.create_text(mx, my - 10, text=t_name, fill="blue")