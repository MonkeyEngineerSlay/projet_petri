 # interface.py
import tkinter as tk
from model import PetriNet # On importe la logique qu'on vient de créer

class PetriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur de Réseau de Petri")
        self.petri_net = PetriNet() # Instance du modèle
        
        # --- Outils (Boutons) ---
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(self.toolbar, text="Ajouter Place", command=self.set_mode_place).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Ajouter Transition", command=self.set_mode_transition).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Tirer (Fire)", command=self.fire_transition).pack(side=tk.LEFT)

        # --- Zone de dessin (Canvas) ---
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        
        # Gestion des clics souris
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.mode = "PLACE" # Mode par défaut
        self.counter_p = 0
        self.counter_t = 0

    def set_mode_place(self):
        self.mode = "PLACE"
        print("Mode: Ajout de Place")

    def set_mode_transition(self):
        self.mode = "TRANSITION"
        print("Mode: Ajout de Transition")

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        
        if self.mode == "PLACE":
            self.draw_place(x, y)
        elif self.mode == "TRANSITION":
            self.draw_transition(x, y)

    def draw_place(self, x, y):
        r = 20 # rayon
        name = f"P{self.counter_p}"
        self.petri_net.add_place(name, 1) # Ajoute au modèle logique
        # Dessine visuellement
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", outline="black")
        self.canvas.create_text(x, y, text=name)
        self.counter_p += 1

    def draw_transition(self, x, y):
        w, h = 15, 40 # dimensions
        name = f"T{self.counter_t}"
        self.petri_net.add_transition(name) # Ajoute au modèle logique
        # Dessine visuellement
        self.canvas.create_rectangle(x-w, y-h, x+w, y+h, fill="black")
        self.canvas.create_text(x, y-h-10, text=name)
        self.counter_t += 1

    def fire_transition(self):
        # Ici il faudra coder la logique pour sélectionner une transition et appeler self.petri_net.fire()
        pass