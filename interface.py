#interface.py
import tkinter as tk
from petri_model import PetriNet
from editor import PetriEditor

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MVC Petri Editor - Avec Déplacement")
        
        self.petri_net = PetriNet()
        self.editor = PetriEditor(self.petri_net, self)
        
        #Données graphiques
        self.canvas_item_to_name = {}
        self.name_to_coords = {}
        self.place_name_to_text_id = {}
        
       #Pour déplacer tout le groupe (Forme + Texte)
        self.name_to_ids = {} 

        #GUI 
        self.toolbar = tk.Frame(root, bg="#ddd")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        #Ajout du bouton MOVE
        self.create_button("Place", "PLACE")
        self.create_button("Transition", "TRANSITION")
        self.create_button("Arc", "ARC")
        self.create_button("DÉPLACER", "MOVE", bg="#aaccff") #Nouveau bouton
        self.create_button("TIRER", "FIRE", bg="orange")
        self.create_button("Reachability", "REACH")

        self.lbl_mode = tk.Label(self.toolbar, text="Mode: PLACE", fg="blue")
        self.lbl_mode.pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        #Bindings (Événements)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)      #Quand on glisse
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release) #Quand on lâche

    def create_button(self, text, mode, bg="SystemButtonFace"):
        tk.Button(self.toolbar, text=text, bg=bg, 
                  command=lambda: self.editor.set_mode(mode)).pack(side=tk.LEFT)

    def update_mode_label(self, text):
        self.lbl_mode.config(text=text)

    #Gestion des événements souris 
    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        item_name = self.canvas_item_to_name.get(item[0]) if item else None
        self.editor.handle_click(event.x, event.y, item_name)

    def on_canvas_drag(self, event):
        #On transmet le mouvement à l'éditeur
        self.editor.handle_drag(event.x, event.y)

    def on_canvas_release(self, event):
        self.editor.handle_release()

    #Méthodes de dessin 
    def draw_place_visual(self, x, y, name, tokens):
        r = 20
        #On donne un tag commun 'name' pour pouvoir tout retrouver facilement
        sid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", width=2)
        tid = self.canvas.create_text(x, y, text=f"{name}\n({tokens})")
        
        self.register_object(name, x, y, [sid, tid], is_place=True)

    def draw_transition_visual(self, x, y, name):
        w, h = 15, 20
        sid = self.canvas.create_rectangle(x-w, y-h, x+w, y+h, fill="black")
        tid = self.canvas.create_text(x, y-h-15, text=name)
        
        self.register_object(name, x, y, [sid, tid], is_place=False)

    def register_object(self, name, x, y, ids, is_place):
        """Helper pour enregistrer les IDs et coords"""
        for i in ids:
            self.canvas_item_to_name[i] = name
        
        self.name_to_ids[name] = ids # On stocke la liste des IDs (Forme + Texte)
        self.name_to_coords[name] = (x, y)
        
        if is_place:
            #Le 2ème ID est le texte
            self.place_name_to_text_id[name] = ids[1]

    def draw_arc_visual(self, source, target):
        x1, y1 = self.name_to_coords[source]
        x2, y2 = self.name_to_coords[target]
        #On ajoute le tag "ARC" pour pouvoir les supprimer facilement lors du redessin
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2, tags="ARC")

    def refresh_tokens(self):
        for name, place in self.petri_net.places.items():
            txt_id = self.place_name_to_text_id.get(name)
            if txt_id:
                self.canvas.itemconfigure(txt_id, text=f"{name}\n({place.tokens})")

    #Méthode de déplacement
    def move_object(self, name, new_x, new_y):
        #1. Mettre à jour les coordonnées mémorisées
        self.name_to_coords[name] = (new_x, new_y)
        
        #2. Calculer le delta (décalage) pour le Canvas.move
        
        ids = self.name_to_ids.get(name)
        if not ids: return

        #Pour simplifier, on redessine ou on déplace. 
        #Ici on va utiliser coords pour recentrer l'objet sur la souris
        
        #Si c'est une Place (Rond)
        if name.startswith("P"):
            r = 20
            self.canvas.coords(ids[0], new_x-r, new_y-r, new_x+r, new_y+r) # Le rond
            self.canvas.coords(ids[1], new_x, new_y) # Le texte
            
        #Si c'est une Transition (Carré)
        elif name.startswith("T"):
            w, h = 15, 20
            self.canvas.coords(ids[0], new_x-w, new_y-h, new_x+w, new_y+h) # Le carré
            self.canvas.coords(ids[1], new_x, new_y-h-15) # Le texte

        # 3. LE PLUS IMPORTANT : Redessiner les Arcs !
        # La méthode simple : on efface tous les arcs et on les refait
        self.redraw_arrows()

    def redraw_arrows(self):
        #Supprime toutes les lignes existantes
        self.canvas.delete("ARC")
        
        #Redemande au modèle quels sont les arcs existants
        for arc in self.petri_net.arcs:
            source_name = arc.source.name
            target_name = arc.target.name
            
            #Redessine
            self.draw_arc_visual(source_name, target_name)

    def show_reachability(self):
        # 1) construire le graphe d'états à partir du marquage courant
        self.petri_net.build_reachability_graph()

        # 2) récupérer une représentation texte
        text = self.petri_net.get_reachability_as_strings()

        # 3) l’afficher dans une nouvelle fenêtre Tk
        win = tk.Toplevel(self.root)
        win.title("Graphe de reachability")
        txt = tk.Text(win, width=80, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED)

    def show_text_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        txt = tk.Text(win, width=80, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", text)
