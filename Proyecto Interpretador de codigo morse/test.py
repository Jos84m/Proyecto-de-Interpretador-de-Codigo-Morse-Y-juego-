#=====================================================================================================
# Zona de importacion de librerias para la creacion de nuesto proyecto
#=====================================================================================================
import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import time
import threading
import json
import math
#=====================================================================================================
# Abecedario de la representacion de las letras en codigo morse y funciones de conversion y puntuacion
#=====================================================================================================
MORSE_CODE = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',    'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..',   'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',   'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-', 'R': '.-.',  'S': '...', 'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----','1': '.----','2': '..---','3': '...--',
    '4': '....-','5': '.....','6': '-....','7': '--...',
    '8': '---..',  '9': '----.',
    ' ': '/'
}
MORSE_REVERSE = {v: k for k, v in MORSE_CODE.items()}
#=================================================================================================================
# Funcion de conversion del texto hacia traduccion de Codigo Morse 
#=================================================================================================================
def text_to_morse(text):
    result = []
    for ch in text.upper():
        if ch in MORSE_CODE:
            result.append(MORSE_CODE[ch])
    return ' '.join(result)    
#=================================================================================================================
# Funcion de Codigo Morse a texto 
#=================================================================================================================
def morse_to_text(morse):
    words = morse.strip().split(' / ')
    result = ''
    for word in words:
        chars = word.strip().split(' ')
        for c in chars:
            result += MORSE_REVERSE.get(c, '?')
        result += ' '
    return result.strip()
#=================================================================================================================
# Funcion de puntaje de las letras correctas en morse
#=================================================================================================================
def score_morse(original, attempt):
    """Score based on character matching"""
    original = original.upper().strip()
    attempt = attempt.upper().strip()
    if not original:
        return 0
    correct = sum(a == b for a, b in zip(original, attempt))
    return int((correct / len(original)) * 100)
#===================================================================================================
# Base de Colores utilizados para nuestra interfaz e juego 
#===================================================================================================
BG_DARK    = "#0A0E1A"
BG_PANEL   = "#111827"
BG_CARD    = "#1A2235"
ACCENT1    = "#00FFD1"   
ACCENT2    = "#FF6B35"   
ACCENT3    = "#FFD700"   
TEXT_PRI   = "#E8EAED"
TEXT_SEC   = "#8892A4"
DOT_COLOR  = "#00FFD1"
DASH_COLOR = "#FF6B35"
LED_ON     = "#FFD700"
LED_OFF    = "#1E2A3A"
RED_COLOR  = "#FF4757"
GREEN_COLOR= "#2ED573"
#======================================================================================================
# Frases a utilizar o frases alatorias
#======================================================================================================
FRASES_DEFAULT = [
    "SOS", "SI", "NO", "HOLA MUNDO",
    "CODIGO MORSE", "JUEGO", "AYUDA",
    "BIEN HECHO", "INTENTA MAS", "PERFECTO"
]
#========================================================================================================
# Clase principal de nuestro juego de intepretacion de codigo morse
#=========================================================================================================
class MorseGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MORSE MASTER")
        self.geometry("1200x780")
        self.resizable(True, True)
        self.configure(bg=BG_DARK)
        # Estado global
        self.frases       = list(FRASES_DEFAULT)
        self.frase_actual = ""
        self.modo_juego   = tk.StringVar(value="escucha")   # "escucha" | "simple"
        self.velocidad    = tk.StringVar(value="A")          # A=0.2s  B=0.3s
        self.turno        = 1                                 # 1 = jugador A, 2 = jugador B
        self.puntaje      = {"A": 0, "B": 0}
        self.rondas       = 0
        self.input_morse_a = ""
        self.input_morse_b = ""
        self.led_estados  = [False] * 16
        self._build_fonts()
        self._build_ui()
        self._animate_leds_idle()
#================================================================================================================
# Funcion de creacion de fuentes para nuestra interfaz ademas de agregar algunas caracteristicas de esto mismo
#================================================================================================================
    def _build_fonts(self):
        self.font_title  = font.Font(family="Courier New", size=22, weight="bold")
        self.font_sub    = font.Font(family="Courier New", size=13, weight="bold")
        self.font_mono   = font.Font(family="Courier New", size=11)
        self.font_big    = font.Font(family="Courier New", size=32, weight="bold")
        self.font_led    = font.Font(family="Courier New", size=10)
        self.font_small  = font.Font(family="Courier New", size=9)
        self.font_btn    = font.Font(family="Courier New", size=11, weight="bold")
#===========================================================================================================================================
# Funcion de creacion de la interfaz grafica de nuestro juego, ademas de agregar las caracteristicas de cada una de las pestañas y botones
#============================================================================================================================================
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill=tk.X, padx=20, pady=(12,0))
        tk.Label(hdr, text="STRANGER TEC", font=self.font_title,
                 bg=BG_DARK, fg=ACCENT1).pack(side=tk.LEFT)
        tk.Label(hdr, text="Juego de Código Morse · 2 Jugadores",
                 font=self.font_small, bg=BG_DARK, fg=TEXT_SEC).pack(side=tk.LEFT, padx=16)
        # Separador decorativo
        sep = tk.Canvas(self, height=2, bg=BG_DARK, highlightthickness=0)
        sep.pack(fill=tk.X, padx=20, pady=4)
        sep.after(100, lambda: self._draw_sep(sep))
        # Notebook (pestañas)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook",            background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",        background=BG_PANEL, foreground=TEXT_SEC,
                        font=("Courier New",11,"bold"), padding=[18,8])
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT1)])
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.tab_config  = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_juego   = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_maqueta = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_frases  = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_ref     = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_config,  text="CONFIG ")
        self.nb.add(self.tab_juego,   text="JUEGO ")
        self.nb.add(self.tab_maqueta, text="MAQUETA ")
        self.nb.add(self.tab_frases,  text="FRASES ")
        self.nb.add(self.tab_ref,     text="REFERENCIA ")
        self._build_tab_config()
        self._build_tab_juego()
        self._build_tab_maqueta()
        self._build_tab_frases()
        self._build_tab_referencia()
#================================================================================================================
    def _draw_sep(self, c):
        c.update_idletasks()
        w = c.winfo_width()
        c.create_line(0, 1, w, 1, fill=ACCENT1, width=1)
#====================================================================================================================================================
# Funcion de creacion de tarjetas para organizar los elementos dentro de la interfaz, ademas de agregar algunas caracteristicas a estas tarjetas
#====================================================================================================================================================
    def _build_tab_config(self):
        p = self.tab_config
        tk.Label(p, text="CONFIGURACIÓN DE PARTIDA", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT1).pack(pady=(18,10))
        outer = tk.Frame(p, bg=BG_DARK)
        outer.pack(expand=True)
        # ── Modo de juego ──
        card1 = self._card(outer, "MODO DE JUEGO")
        card1.pack(side=tk.LEFT, padx=18, pady=8, fill=tk.Y)
        tk.Radiobutton(card1, text="🎧  Escucha y Transmisión",
                       variable=self.modo_juego, value="escucha",
                       font=self.font_mono, bg=BG_CARD, fg=TEXT_PRI,
                       selectcolor=BG_CARD, activebackground=BG_CARD,
                       activeforeground=ACCENT1).pack(anchor=tk.W, pady=6, padx=10)
        tk.Radiobutton(card1, text="📡  Transmisión Simple",
                       variable=self.modo_juego, value="simple",
                       font=self.font_mono, bg=BG_CARD, fg=TEXT_PRI,
                       selectcolor=BG_CARD, activebackground=BG_CARD,
                       activeforeground=ACCENT1).pack(anchor=tk.W, pady=6, padx=10)
        desc_modo = tk.Label(card1,
            text="Escucha y Transmisión:\nAmbos jugadores reciben la misma\nfrase y la codifican en Morse.\n\n"
                 "Transmisión Simple:\nDesde la maqueta se transmite un\nmensaje y la app valida.",
            font=self.font_small, bg=BG_CARD, fg=TEXT_SEC,
            justify=tk.LEFT, wraplength=240)
        desc_modo.pack(padx=10, pady=8)
        # ── Velocidad (Unidad) ──
        card2 = self._card(outer, "VELOCIDAD (UNIDAD BASE)")
        card2.pack(side=tk.LEFT, padx=18, pady=8, fill=tk.Y)
        for lbl, val, desc in [
            ("Unidad A  —  0.2 seg", "A", "Rápido"),
            ("Unidad B  —  0.3 seg", "B", "Normal"),
        ]:
            tk.Radiobutton(card2, text=lbl,
                           variable=self.velocidad, value=val,
                           font=self.font_mono, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=BG_CARD, activebackground=BG_CARD,
                           activeforeground=ACCENT2).pack(anchor=tk.W, pady=6, padx=10)
        # Tabla de tiempos
        tk.Label(card2, text="Tiempos según velocidad:",
                 font=self.font_small, bg=BG_CARD, fg=TEXT_SEC).pack(padx=10, pady=(10,2))
        tabla_frame = tk.Frame(card2, bg=BG_CARD)
        tabla_frame.pack(padx=10, pady=4)
        headers = ["Elemento","Unid.","A (seg)","B (seg)"]
        rows = [
            ("Punto  (·)",  "1", "0.20", "0.30"),
            ("Raya   (—)",  "3", "0.60", "0.90"),
            ("Sep. símbolo","1", "0.20", "0.30"),
            ("Sep. carácter","3","0.60", "0.90"),
            ("Sep. palabra","7", "1.40", "2.10"),
        ]
        for ci, h in enumerate(headers):
            tk.Label(tabla_frame, text=h, font=self.font_small,
                     bg=BG_DARK, fg=ACCENT1, width=12,
                     relief=tk.FLAT, padx=4).grid(row=0, column=ci, padx=1, pady=1)
        for ri, row in enumerate(rows, 1):
            for ci, cell in enumerate(row):
                bg = BG_CARD if ri % 2 == 0 else "#16202E"
                tk.Label(tabla_frame, text=cell, font=self.font_small,
                         bg=bg, fg=TEXT_PRI, width=12,
                         relief=tk.FLAT, padx=4).grid(row=ri, column=ci, padx=1, pady=1)
        # ── Medio de presentación ──
        card3 = self._card(outer, "MEDIO DE PRESENTACIÓN")
        card3.pack(side=tk.LEFT, padx=18, pady=8, fill=tk.Y)
        self.medio = tk.StringVar(value="luz")
        for lbl, val in [("Señales Luminosas (LEDs)", "luz"),
                         (" Señales Sonoras (Buzzer)",  "sonido")]:
            tk.Radiobutton(card3, text=lbl,
                           variable=self.medio, value=val,
                           font=self.font_mono, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=BG_CARD, activebackground=BG_CARD,
                           activeforeground=ACCENT3).pack(anchor=tk.W, pady=6, padx=10)
        tk.Label(card3, text="Modo Conexión:",
                 font=self.font_small, bg=BG_CARD, fg=TEXT_SEC).pack(padx=10, pady=(14,2), anchor=tk.W)
        self.modo_conn = tk.StringVar(value="local")
        for lbl, val in [("Local (USB Serial)", "local"),
                         (" Versus (WiFi)", "versus")]:
            tk.Radiobutton(card3, text=lbl,
                           variable=self.modo_conn, value=val,
                           font=self.font_mono, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=BG_CARD, activebackground=BG_CARD,
                           activeforeground=ACCENT1).pack(anchor=tk.W, pady=4, padx=10)
        # Botón iniciar
        btn_frame = tk.Frame(p, bg=BG_DARK)
        btn_frame.pack(pady=18)
        self._neon_btn(btn_frame, "▶  INICIAR PARTIDA", ACCENT1, self._iniciar_juego).pack()
#================================================================================================================================================================================
# Funcion de creacion de la interfaz grafica de nuestro juego, ademas de agregar las caracteristicas de cada una de las pestañas y botones, en este caso para la pestaña del juego
#===============================================================================================================================================================================
    def _build_tab_juego(self):
        p = self.tab_juego

        # ── Status bar ──
        status_bar = tk.Frame(p, bg=BG_PANEL, height=48)
        status_bar.pack(fill=tk.X, padx=10, pady=(10,4))
        status_bar.pack_propagate(False)

        self.lbl_turno = tk.Label(status_bar, text="Turno: —",
                                  font=self.font_sub, bg=BG_PANEL, fg=ACCENT1)
        self.lbl_turno.pack(side=tk.LEFT, padx=16)

        self.lbl_score = tk.Label(status_bar,
                                  text="Jugador A: 0 pts  |  Jugador B: 0 pts",
                                  font=self.font_mono, bg=BG_PANEL, fg=TEXT_PRI)
        self.lbl_score.pack(side=tk.LEFT, padx=30)

        self.lbl_ronda = tk.Label(status_bar, text="Ronda 0",
                                  font=self.font_mono, bg=BG_PANEL, fg=TEXT_SEC)
        self.lbl_ronda.pack(side=tk.RIGHT, padx=16)

        # ── Frase actual ──
        frase_card = self._card(p, "FRASE ACTUAL")
        frase_card.pack(fill=tk.X, padx=16, pady=4)

        self.lbl_frase = tk.Label(frase_card, text="— Presiona INICIAR —",
                                   font=self.font_big, bg=BG_CARD, fg=ACCENT3)
        self.lbl_frase.pack(pady=10)

        self.lbl_morse_frase = tk.Label(frase_card, text="",
                                        font=self.font_mono, bg=BG_CARD, fg=TEXT_SEC)
        self.lbl_morse_frase.pack(pady=(0,8))

        # ── Panel jugadores ──
        jugadores_frame = tk.Frame(p, bg=BG_DARK)
        jugadores_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # Jugador A
        card_a = self._card(jugadores_frame, "JUGADOR A  (Teclado)")
        card_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        self._build_player_panel(card_a, "A")

        # Jugador B
        card_b = self._card(jugadores_frame, "JUGADOR B  (Maqueta/Botones)")
        card_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        self._build_player_panel(card_b, "B")

        # ── Botones acción ──
        btn_row = tk.Frame(p, bg=BG_DARK)
        btn_row.pack(pady=10)
        self._neon_btn(btn_row, " NUEVA FRASE", ACCENT1, self._nueva_frase).pack(side=tk.LEFT, padx=8)
        self._neon_btn(btn_row, " REPRODUCIR MORSE", ACCENT3, self._reproducir_morse).pack(side=tk.LEFT, padx=8)
        self._neon_btn(btn_row, " EVALUAR RONDA", GREEN_COLOR, self._evaluar_ronda).pack(side=tk.LEFT, padx=8)
        self._neon_btn(btn_row, " REINICIAR", ACCENT2, self._reiniciar).pack(side=tk.LEFT, padx=8)
#================================================================================================================
#Funcion de la creacion de la interfaz grafica de nuestro juego, ademas de agregar las caracteristicas de cada una de las pestañas y botones, en este caso para los paneles de cada jugador
#================================================================================================================

    def _build_player_panel(self, parent, jugador):
        color = ACCENT1 if jugador == "A" else ACCENT2

        # Indicador de turno activo
        turno_lbl = tk.Label(parent, text="⬤ EN ESPERA",
                             font=self.font_small, bg=BG_CARD, fg=TEXT_SEC)
        turno_lbl.pack(pady=(4,2))
        if jugador == "A":
            self.turno_lbl_a = turno_lbl
        else:
            self.turno_lbl_b = turno_lbl

        # Input Morse
        tk.Label(parent, text="Entrada Morse (. - / espacio):",
                 font=self.font_small, bg=BG_CARD, fg=TEXT_SEC).pack(anchor=tk.W, padx=8, pady=(8,2))

        input_frame = tk.Frame(parent, bg=BG_CARD)
        input_frame.pack(fill=tk.X, padx=8)

        entry = tk.Text(input_frame, height=3, width=30,
                        font=self.font_mono, bg="#0D1526", fg=color,
                        insertbackground=color, relief=tk.FLAT,
                        bd=0, padx=6, pady=6)
        entry.pack(fill=tk.X)

        if jugador == "A":
            self.entry_a = entry
        else:
            self.entry_b = entry

        # Botones morse rápido (solo jugador A desde PC)
        if jugador == "A":
            morse_btns = tk.Frame(parent, bg=BG_CARD)
            morse_btns.pack(pady=4)
            for sym, lbl in [(".", "•  PUNTO"), ("-", "—  RAYA"),
                              (" ", "ESPACIO"), ("/", "/  PALABRA")]:
                tk.Button(morse_btns, text=lbl, font=self.font_small,
                          bg="#1E2A3A", fg=color, relief=tk.FLAT,
                          activebackground=BG_PANEL, activeforeground=color,
                          command=lambda s=sym, e=entry: self._insert_morse(e, s),
                          padx=8, pady=4).pack(side=tk.LEFT, padx=2)
            tk.Button(morse_btns, text="⌫ BORRAR", font=self.font_small,
                      bg="#2A1515", fg=RED_COLOR, relief=tk.FLAT,
                      activebackground=BG_PANEL, activeforeground=RED_COLOR,
                      command=lambda e=entry: e.delete("1.0", tk.END),
                      padx=8, pady=4).pack(side=tk.LEFT, padx=2)

        # Decodificación en tiempo real
        tk.Label(parent, text="Decodificado:", font=self.font_small,
                 bg=BG_CARD, fg=TEXT_SEC).pack(anchor=tk.W, padx=8, pady=(6,0))
        decoded_lbl = tk.Label(parent, text="—", font=self.font_sub,
                               bg=BG_CARD, fg=color)
        decoded_lbl.pack(anchor=tk.W, padx=8)

        if jugador == "A":
            self.decoded_a = decoded_lbl
        else:
            self.decoded_b = decoded_lbl

        # Barra de progreso / puntaje
        score_lbl = tk.Label(parent, text="Puntaje: —",
                             font=self.font_sub, bg=BG_CARD, fg=ACCENT3)
        score_lbl.pack(pady=(6,4))
        if jugador == "A":
            self.score_lbl_a = score_lbl
        else:
            self.score_lbl_b = score_lbl

        # Bind actualización en tiempo real
        entry.bind("<KeyRelease>", lambda e, j=jugador: self._update_decoded(j))
#================================================================================================================
#Funcion de la creacion de la interfaz grafica de nuestro juego, ademas de agregar las caracteristicas de cada una de las pestañas y botones, en este caso para la pestaña de la maqueta
#================================================================================================================
    def _build_tab_maqueta(self):
        p = self.tab_maqueta
        tk.Label(p, text="SIMULADOR DE MAQUETA", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT1).pack(pady=(14,6))
        tk.Label(p, text="Visualización de 16 LEDs + Buzzer (Raspberry Pi Pico W)",
                 font=self.font_small, bg=BG_DARK, fg=TEXT_SEC).pack()

        main = tk.Frame(p, bg=BG_DARK)
        main.pack(expand=True, pady=10)

        # ── Panel LEDs ──
        led_card = self._card(main, "PANEL 16 LEDs")
        led_card.pack(side=tk.LEFT, padx=18, pady=8)

        led_grid = tk.Frame(led_card, bg=BG_CARD)
        led_grid.pack(padx=16, pady=12)

        self.led_canvas_list = []
        for i in range(16):
            row, col = divmod(i, 8)
            c = tk.Canvas(led_grid, width=44, height=44,
                          bg=BG_CARD, highlightthickness=0)
            c.grid(row=row, column=col, padx=5, pady=5)
            oval = c.create_oval(4, 4, 40, 40, fill=LED_OFF, outline="#2A3A4A", width=2)
            num  = c.create_text(22, 22, text=str(i+1),
                                 font=self.font_led, fill="#3A4A5A")
            self.led_canvas_list.append((c, oval, num))

        # Número actual mostrado
        self.lbl_num_led = tk.Label(led_card, text="—",
                                    font=self.font_big, bg=BG_CARD, fg=LED_ON)
        self.lbl_num_led.pack(pady=6)
        tk.Label(led_card, text="Número representado",
                 font=self.font_small, bg=BG_CARD, fg=TEXT_SEC).pack()

        # Botones LED test
        led_ctrl = tk.Frame(led_card, bg=BG_CARD)
        led_ctrl.pack(pady=10)
        for i in range(10):
            tk.Button(led_ctrl, text=str(i), font=self.font_small,
                      bg="#1E2A3A", fg=LED_ON, relief=tk.FLAT,
                      activebackground=BG_PANEL,
                      command=lambda n=i: self._mostrar_numero_led(n),
                      width=4, pady=4).pack(side=tk.LEFT, padx=2)

        # ── Panel Morse Visual ──
        morse_card = self._card(main, "TRANSMISIÓN MORSE VISUAL")
        morse_card.pack(side=tk.LEFT, padx=18, pady=8, fill=tk.BOTH, expand=True)

        self.morse_canvas = tk.Canvas(morse_card, width=420, height=80,
                                      bg="#080D18", highlightthickness=0)
        self.morse_canvas.pack(padx=12, pady=10)

        self.lbl_morse_visual = tk.Label(morse_card, text="Presiona REPRODUCIR en la pestaña JUEGO",
                                         font=self.font_small, bg=BG_CARD, fg=TEXT_SEC,
                                         wraplength=320)
        self.lbl_morse_visual.pack(pady=4)

        # Simulador botones de maqueta
        btn_card = self._card(morse_card, "BOTONES JUGADOR B (Simulados)")
        btn_card.pack(fill=tk.X, padx=10, pady=8)

        btns = tk.Frame(btn_card, bg=BG_CARD)
        btns.pack(pady=8)

        self.btn_dot  = tk.Button(btns, text="●\nPUNTO",  font=self.font_btn,
                                  bg=DOT_COLOR, fg=BG_DARK, relief=tk.FLAT,
                                  width=9, height=3,
                                  command=lambda: self._sim_boton("."))
        self.btn_dot.pack(side=tk.LEFT, padx=8)

        self.btn_dash = tk.Button(btns, text="━\nRAYA",   font=self.font_btn,
                                  bg=DASH_COLOR, fg=BG_DARK, relief=tk.FLAT,
                                  width=9, height=3,
                                  command=lambda: self._sim_boton("-"))
        self.btn_dash.pack(side=tk.LEFT, padx=8)

        self.btn_space = tk.Button(btns, text="□\nESPACIO", font=self.font_btn,
                                   bg="#5A6A7A", fg=TEXT_PRI, relief=tk.FLAT,
                                   width=9, height=3,
                                   command=lambda: self._sim_boton(" "))
        self.btn_space.pack(side=tk.LEFT, padx=8)

        self.btn_word = tk.Button(btns, text="/\nPALABRA", font=self.font_btn,
                                  bg="#3A4A5A", fg=TEXT_PRI, relief=tk.FLAT,
                                  width=9, height=3,
                                  command=lambda: self._sim_boton("/"))
        self.btn_word.pack(side=tk.LEFT, padx=8)

        tk.Button(btns, text="⌫\nBORRAR", font=self.font_btn,
                  bg="#4A1515", fg=RED_COLOR, relief=tk.FLAT,
                  width=9, height=3,
                  command=self._sim_borrar).pack(side=tk.LEFT, padx=8)
#=================================================================================================================================================
# Funcion de creacion de las frases a utilizar en nuestro juego para que nuestro usario pueda practicar la interpretacion de codigo morse
#=================================================================================================================================================
    def _build_tab_frases(self):
        p = self.tab_frases
        tk.Label(p, text="LISTA DE FRASES", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT1).pack(pady=(14,4))
        tk.Label(p, text="Máximo 10 frases · Máximo 16 caracteres cada una",
                 font=self.font_small, bg=BG_DARK, fg=TEXT_SEC).pack()
        cols = tk.Frame(p, bg=BG_DARK)
        cols.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        # Lista
        list_card = self._card(cols, "FRASES DISPONIBLES")
        list_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

        self.listbox_frases = tk.Listbox(list_card, font=self.font_mono,
                                         bg="#0D1526", fg=ACCENT1,
                                         selectbackground=ACCENT1,
                                         selectforeground=BG_DARK,
                                         relief=tk.FLAT, bd=0,
                                         height=12, width=22)
        self.listbox_frases.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._refresh_listbox()
        # Editor
        edit_card = self._card(cols, "AGREGAR / EDITAR")
        edit_card.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        tk.Label(edit_card, text="Nueva frase (max 16 chars):",
                 font=self.font_small, bg=BG_CARD, fg=TEXT_SEC).pack(anchor=tk.W, padx=10, pady=(10,2))

        self.entry_nueva_frase = tk.Entry(edit_card, font=self.font_mono,
                                          bg="#0D1526", fg=ACCENT1,
                                          insertbackground=ACCENT1,
                                          relief=tk.FLAT, bd=0, width=22)
        self.entry_nueva_frase.pack(padx=10, pady=4, ipady=6, fill=tk.X)

        self.lbl_preview_morse = tk.Label(edit_card, text="Morse: —",
                                          font=self.font_small, bg=BG_CARD,
                                          fg=TEXT_SEC, wraplength=220, justify=tk.LEFT)
        self.lbl_preview_morse.pack(padx=10, pady=4)
        self.entry_nueva_frase.bind("<KeyRelease>", self._preview_morse)

        btn_col = tk.Frame(edit_card, bg=BG_CARD)
        btn_col.pack(pady=6)
        self._neon_btn(btn_col, " AGREGAR", ACCENT1, self._agregar_frase).pack(fill=tk.X, pady=3)
        self._neon_btn(btn_col, "ELIMINAR", RED_COLOR, self._eliminar_frase).pack(fill=tk.X, pady=3)
        self._neon_btn(btn_col, " RESTAURAR", TEXT_SEC, self._restaurar_frases).pack(fill=tk.X, pady=3)

        # Tabla morse
        morse_card = self._card(cols, "MORSE COMPLETO")
        morse_card.pack(side=tk.LEFT, fill=tk.BOTH, padx=8)

        tabla = tk.Text(morse_card, font=self.font_small,
                        bg="#0D1526", fg=TEXT_PRI, relief=tk.FLAT,
                        bd=0, width=24, height=14, padx=6, pady=6)
        tabla.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        tabla.config(state=tk.NORMAL)
        for ch, code in sorted(MORSE_CODE.items()):
            if ch != ' ':
                tabla.insert(tk.END, f"  {ch}  →  {code}\n")
        tabla.config(state=tk.DISABLED)
#=================================================================================================================
# Funcion de creacion de las referencias del codigo morse para que nuestro usuario pueda consultar cada una de las letras y numeros con su respectiva representacion en codigo morse
#================================================================================================================
    def _build_tab_referencia(self):
        p = self.tab_ref
        tk.Label(p, text="REFERENCIA DE CÓDIGO MORSE", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT1).pack(pady=(14,4))

        scroll_frame = tk.Frame(p, bg=BG_DARK)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        canvas = tk.Canvas(scroll_frame, bg=BG_DARK, highlightthickness=0)
        scroll = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        inner  = tk.Frame(canvas, bg=BG_DARK)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Grid de letras
        letters = [(ch, MORSE_CODE[ch]) for ch in sorted(MORSE_CODE) if ch.isalpha()]
        digits  = [(ch, MORSE_CODE[ch]) for ch in sorted(MORSE_CODE) if ch.isdigit()]

        tk.Label(inner, text="LETRAS", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT1).grid(row=0, column=0, columnspan=7,
                                               pady=8, sticky=tk.W, padx=8)
        for i, (ch, code) in enumerate(letters):
            row, col = divmod(i, 7)
            cell = tk.Frame(inner, bg=BG_CARD, padx=10, pady=8)
            cell.grid(row=row+1, column=col, padx=4, pady=4, sticky=tk.W+tk.E)
            tk.Label(cell, text=ch, font=self.font_big,
                     bg=BG_CARD, fg=ACCENT1, width=2).pack()
            dots_frame = tk.Frame(cell, bg=BG_CARD)
            dots_frame.pack()
            self._render_morse_dots(dots_frame, code)
            tk.Label(cell, text=code, font=self.font_small,
                     bg=BG_CARD, fg=TEXT_SEC).pack()

        row_offset = (len(letters) // 7) + 2
        tk.Label(inner, text="NÚMEROS", font=self.font_sub,
                 bg=BG_DARK, fg=ACCENT2).grid(row=row_offset, column=0,
                                               columnspan=7, pady=8,
                                               sticky=tk.W, padx=8)
        for i, (ch, code) in enumerate(digits):
            row, col = divmod(i, 7)
            cell = tk.Frame(inner, bg=BG_CARD, padx=10, pady=8)
            cell.grid(row=row_offset+row+1, column=col, padx=4, pady=4, sticky=tk.W+tk.E)
            tk.Label(cell, text=ch, font=self.font_big,
                     bg=BG_CARD, fg=ACCENT2, width=2).pack()
            dots_frame = tk.Frame(cell, bg=BG_CARD)
            dots_frame.pack()
            self._render_morse_dots(dots_frame, code)
            tk.Label(cell, text=code, font=self.font_small,
                     bg=BG_CARD, fg=TEXT_SEC).pack
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
#=================================================================================================================
# Funcion de creacion de las representaciones visuales de los puntos y rayas del codigo morse para la pestaña de referencia, ademas de agregar algunas caracteristicas a estas representaciones
#==================================================================================================================
    def _render_morse_dots(self, parent, code):
        for sym in code:
            if sym == '.':
                c = tk.Canvas(parent, width=12, height=12,
                              bg=BG_CARD, highlightthickness=0)
                c.create_oval(1,1,11,11, fill=DOT_COLOR, outline="")
                c.pack(side=tk.LEFT, padx=1)
            elif sym == '-':
                c = tk.Canvas(parent, width=26, height=12,
                              bg=BG_CARD, highlightthickness=0)
                c.create_rectangle(1,4,25,8, fill=DASH_COLOR, outline="")
                c.pack(side=tk.LEFT, padx=1)
#=================================================================================================================
# Funcion de iniciar nuestro juego, esta funcion se encarga de reiniciar los puntajes, seleccionar una nueva frase aleatoria de la lista de frases y actualizar la interfaz para mostrar la nueva frase y el código morse correspondiente, ademas de configurar el turno del jugador A para que comience la partida
#=================================================================================================================
    def _iniciar_juego(self):
        self.puntaje = {"A": 0, "B": 0}
        self.rondas  = 0
        self._nueva_frase()
        self.nb.select(1)
# Carga de nueva frase y actualización de interfaz
    def _nueva_frase(self):
        if not self.frases:
            messagebox.showwarning("Sin frases", "Agrega frases en la pestaña FRASES.")
            return
        self.frase_actual = random.choice(self.frases)
        self.rondas += 1
        morse = text_to_morse(self.frase_actual)
        self.lbl_frase.config(text=self.frase_actual)
        self.lbl_morse_frase.config(text=morse)
        self.lbl_ronda.config(text=f"Ronda {self.rondas}")
        self.entry_a.delete("1.0", tk.END)
        self.entry_b.delete("1.0", tk.END)
        self.decoded_a.config(text="—")
        self.decoded_b.config(text="—")
        self.score_lbl_a.config(text="Puntaje: —")
        self.score_lbl_b.config(text="Puntaje: —")
        self._set_turno(1)
# Configuración de turno
    def _set_turno(self, t):
        self.turno = t
        if t == 1:
            self.lbl_turno.config(text="Turno: JUGADOR A")
            self.turno_lbl_a.config(text="TURNO ACTIVO", fg=GREEN_COLOR)
            self.turno_lbl_b.config(text="EN ESPERA",    fg=TEXT_SEC)
        else:
            self.lbl_turno.config(text="Turno: JUGADOR B")
            self.turno_lbl_a.config(text="EN ESPERA",    fg=TEXT_SEC)
            self.turno_lbl_b.config(text="TURNO ACTIVO", fg=GREEN_COLOR)
# Actualización de decodificación en tiempo real
    def _update_decoded(self, jugador):
        entry = self.entry_a if jugador == "A" else self.entry_b
        label = self.decoded_a if jugador == "A" else self.decoded_b
        raw = entry.get("1.0", tk.END).strip()
        try:
            decoded = morse_to_text(raw) if raw else "—"
        except:
            decoded = "?"
        label.config(text=decoded if decoded else "—")
# Simulación botones jugador A
    def _insert_morse(self, entry, sym):
        entry.insert(tk.END, sym)
        self._update_decoded("A")
# Simulación botones jugador B
    def _evaluar_ronda(self):
        if not self.frase_actual:
            messagebox.showinfo("Info", "Primero inicia una partida.")
            return
        morse_a_raw  = self.entry_a.get("1.0", tk.END).strip()
        morse_b_raw  = self.entry_b.get("1.0", tk.END).strip()
        decoded_a    = morse_to_text(morse_a_raw) if morse_a_raw else ""
        decoded_b    = morse_to_text(morse_b_raw) if morse_b_raw else ""
        score_a      = score_morse(self.frase_actual, decoded_a)
        score_b      = score_morse(self.frase_actual, decoded_b)
        self.puntaje["A"] += score_a
        self.puntaje["B"] += score_b
        self.score_lbl_a.config(text=f"Puntaje: {score_a}%")
        self.score_lbl_b.config(text=f"Puntaje: {score_b}%")
        self.lbl_score.config(
            text=f"Jugador A: {self.puntaje['A']} pts  |  Jugador B: {self.puntaje['B']} pts"
        )
        ganador = "A" if score_a > score_b else ("B" if score_b > score_a else "EMPATE")
        ganador_txt = f"Jugador {ganador}" if ganador != "EMPATE" else "¡EMPATE!"
        msg = (f" {ganador_txt} gana la ronda!\n\n"
               f"Frase original:  {self.frase_actual}\n\n"
               f"Jugador A  →  {decoded_a or '(sin entrada)'}  →  {score_a}%\n"
               f"Jugador B  →  {decoded_b or '(sin entrada)'}  →  {score_b}%\n\n"
               f"Puntos acumulados:\n"
               f"  A: {self.puntaje['A']}  |  B: {self.puntaje['B']}")
        messagebox.showinfo("Resultado de la Ronda", msg)
# Función para reiniciar el juego y limpiar todos los puntajes, rondas, frases y entradas para comenzar una nueva partida desde cero
    def _reiniciar(self):
        self.puntaje = {"A": 0, "B": 0}
        self.rondas  = 0
        self.frase_actual = ""
        self.lbl_frase.config(text="— Presiona INICIAR —")
        self.lbl_morse_frase.config(text="")
        self.lbl_score.config(text="Jugador A: 0 pts  |  Jugador B: 0 pts")
        self.lbl_ronda.config(text="Ronda 0")
        self.entry_a.delete("1.0", tk.END)
        self.entry_b.delete("1.0", tk.END)
        self.decoded_a.config(text="—")
        self.decoded_b.config(text="—")
        self.score_lbl_a.config(text="Puntaje: —")
        self.score_lbl_b.config(text="Puntaje: —")
        self.lbl_turno.config(text="Turno: —")
#==================================================================================================================
# Función para reproducir el código morse de la frase actual utilizando una animación visual en el canvas y simulando el encendido de LEDs, esta función se ejecuta en un hilo separado para no bloquear la interfaz mientras se reproduce el morse
#==================================================================================================================
    def _reproducir_morse(self):
        if not self.frase_actual:
            messagebox.showinfo("Info", "Primero selecciona una frase.")
            return
        t = threading.Thread(target=self._play_morse_thread, daemon=True)
        t.start()
# Función que se ejecuta en un hilo separado para reproducir el código morse de la frase actual, esta función se encarga de convertir la frase a morse, mostrar una animación visual en el canvas y simular el encendido de LEDs para representar los puntos y rayas del código morse
    def _play_morse_thread(self):
        unit = 0.2 if self.velocidad.get() == "A" else 0.3
        morse = text_to_morse(self.frase_actual)
        self.lbl_morse_visual.config(text=f"Reproduciendo: {morse}")
        symbols = morse.split(' ')
        x = 10
        self.morse_canvas.delete("all")
        for sym in symbols:
            if sym == '/':
                x += int(7 * unit * 60)
                continue
            for i, ch in enumerate(sym):
                if ch == '.':
                    w = int(unit * 60)
                    self.morse_canvas.create_rectangle(x, 20, x+w, 60,
                                                       fill=DOT_COLOR, outline="")
                    self._led_on()
                    time.sleep(unit)
                    self._led_off()
                    time.sleep(unit)
                    x += w + 4
                elif ch == '-':
                    w = int(3 * unit * 60)
                    self.morse_canvas.create_rectangle(x, 20, x+w, 60,
                                                       fill=DASH_COLOR, outline="")
                    self._led_on()
                    time.sleep(3 * unit)
                    self._led_off()
                    time.sleep(unit)
                    x += w + 4
            x += int(3 * unit * 60)
        self.lbl_morse_visual.config(text="✔ Reproducción completada")
# Funciones para simular el encendido y apagado de los LEDs en la pestaña de maqueta, estas funciones se utilizan durante la reproducción del código morse para representar visualmente los puntos y rayas del código morse
    def _led_on(self):
        for c, oval, num in self.led_canvas_list:
            c.itemconfig(oval, fill=LED_ON)
# Función para apagar todos los LEDs, esta función se utiliza para simular el apagado de los LEDs después de mostrar cada punto o raya durante la reproducción del código morse
    def _led_off(self):
        for c, oval, num in self.led_canvas_list:
            c.itemconfig(oval, fill=LED_OFF)
# Función para mostrar un número específico en los LEDs, esta función se utiliza para representar visualmente los números del 0 al 9 utilizando los primeros 4 LEDs, donde cada LED representa un bit del número en formato binario
    def _mostrar_numero_led(self, n):
        bits = f"{n:04b}"
        self.lbl_num_led.config(text=str(n))
        for i, (c, oval, num) in enumerate(self.led_canvas_list):
            if i < 4:
                on = bits[i] == '1'
                c.itemconfig(oval, fill=LED_ON if on else LED_OFF)
            else:
                c.itemconfig(oval, fill=LED_OFF)
# Función para animar los LEDs en estado idle, esta función muestra una animación suave que recorre los LEDs encendiéndolos uno por uno y luego apagándolos, esta función se puede activar para mostrar una animación visual cuando no hay una partida activa
    def _animate_leds_idle(self):
        def tick(idx=0):
            for i, (c, oval, num) in enumerate(self.led_canvas_list):
                dist = abs(i - idx % 16)
                if dist < 2:
                    c.itemconfig(oval, fill=ACCENT1)
                else:
                    c.itemconfig(oval, fill=LED_OFF)
            self.after(80, lambda: tick(idx+1))
        # Solo mostrar idle si no hay partida activa
        # tick()  # Descomenta para activar animación idle
#==================================================================================================================
# Funciones para simular la entrada de código morse utilizando los botones en la pestaña de maqueta, estas funciones se encargan de insertar el símbolo correspondiente en el campo de texto del jugador B y actualizar la decodificación en tiempo real para mostrar el texto decodificado a medida que se ingresan los símbolos
#==================================================================================================================
    def _sim_boton(self, sym):
        self.entry_b.insert(tk.END, sym)
        self._update_decoded("B")
# Función para simular el borrado de la entrada de código morse del jugador B, esta función se utiliza para limpiar el campo de texto del jugador B y restablecer la decodificación a su estado inicial
    def _sim_borrar(self):
        self.entry_b.delete("1.0", tk.END)
        self.decoded_b.config(text="—")
 #===================================================================================================================
 # Funciones para gestionar la lista de frases disponibles en el juego, estas funciones permiten agregar nuevas frases, eliminar frases seleccionadas y restaurar la lista de frases a su estado predeterminado, además de actualizar la interfaz para reflejar los cambios en la lista de frases   
 #===================================================================================================================
    def _refresh_listbox(self):
        self.listbox_frases.delete(0, tk.END)
        for i, f in enumerate(self.frases, 1):
            self.listbox_frases.insert(tk.END, f"  {i:2}.  {f}")
# Función para mostrar una vista previa del código morse de la nueva frase que se está ingresando en el campo de texto, esta función se activa cada vez que se suelta una tecla en el campo de texto y muestra la representación en código morse de los primeros 16 caracteres de la frase ingresada
    def _preview_morse(self, _=None):
        txt = self.entry_nueva_frase.get().strip()
        if txt:
            m = text_to_morse(txt[:16])
            self.lbl_preview_morse.config(text=f"Morse:\n{m}")
        else:
            self.lbl_preview_morse.config(text="Morse: —")
# Función para agregar una nueva frase a la lista de frases disponibles, esta función se activa al presionar el botón de agregar y verifica que la frase ingresada no esté vacía, no exceda los 16 caracteres y que no se haya alcanzado el límite de 10 frases antes de agregarla a la lista y actualizar la interfaz
    def _agregar_frase(self):
        txt = self.entry_nueva_frase.get().strip().upper()
        if not txt:
            return
        if len(txt) > 16:
            messagebox.showwarning("Muy larga", "Máximo 16 caracteres.")
            return
        if len(self.frases) >= 10:
            messagebox.showwarning("Límite", "Máximo 10 frases.")
            return
        self.frases.append(txt)
        self._refresh_listbox()
        self.entry_nueva_frase.delete(0, tk.END)
# Función para eliminar la frase seleccionada en la lista de frases, esta función se activa al presionar el botón de eliminar y verifica que se haya seleccionado una frase antes de eliminarla de la lista y actualizar la interfaz
    def _eliminar_frase(self):
        sel = self.listbox_frases.curselection()
        if not sel:
            return
        idx = sel[0]
        del self.frases[idx]
        self._refresh_listbox()
# Función para restaurar la lista de frases a su estado predeterminado, esta función se activa al presionar el botón de restaurar y restablece la lista de frases a las frases predeterminadas definidas en el código, además de actualizar la interfaz para reflejar los cambios
    def _restaurar_frases(self):
        self.frases = list(FRASES_DEFAULT)
        self._refresh_listbox()
# Función para crear un "card" o panel con un título, esta función se utiliza para crear secciones visuales en la interfaz con un fondo oscuro y un borde de acento, además de mostrar un título en la parte superior del panel para identificar su contenido
    def _card(self, parent, title):
        frame = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=ACCENT1,
                         highlightthickness=1)
        tk.Label(frame, text=f"  {title}  ", font=self.font_small,
                 bg=BG_PANEL, fg=ACCENT1).pack(fill=tk.X)
        return frame

    def _neon_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=self.font_btn,
                        bg=BG_PANEL, fg=color,
                        activebackground=color, activeforeground=BG_DARK,
                        relief=tk.FLAT, bd=0, padx=18, pady=8,
                        highlightbackground=color, highlightthickness=1,
                        command=command)
        return btn
# ==================================================================================================================
# Función principal para iniciar la aplicación, esta función crea una instancia de la clase MorseGame y ejecuta el bucle principal de la interfaz gráfica para mostrar la ventana del juego y permitir la interacción del usuario con las diferentes pestañas y funcionalidades del juego
# ==================================================================================================================
if __name__ == "__main__":
    app = MorseGame()
    app.mainloop()
