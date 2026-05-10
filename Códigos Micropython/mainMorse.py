from machine import Pin
import time
import sys
import uselect

# -----------------------------------------------------
# Configuración para leer datos del puerto serial (PC)
# -----------------------------------------------------
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

# Esta función revisa si hay datos que llegan desde la PC
# Si hay un carácter disponible, lo devuelve; si no, entonces no devuelve nada
def leer_serial():
    if poll.poll(0):
        return sys.stdin.read(1)
    return None

# --------------------------------
# Pines
# --------------------------------
data = Pin(1, Pin.OUT)  
clock = Pin(0, Pin.OUT)   
boton = Pin(15, Pin.IN, Pin.PULL_DOWN)   
buzzer = Pin(14, Pin.OUT)                
switch_modo = Pin(16, Pin.IN, Pin.PULL_DOWN)  

# --------------------------------
# Tiempo Morse
# --------------------------------
UNIDAD = 0.2   # Duración básica de un punto
UMBRAL = 0.4   # Límite para diferenciar punto de raya

# --------------------------------
# LEDs de la matriz
# --------------------------------
#Se asignan 3 pines para las tres filas
FILA1 = 13
FILA2 = 14
FILA3 = 15

# -----------------------------------------------------------
# Función que genera un pulso en el reloj
# Sirve para indicar al receptor cuándo debe leer el dato
# -----------------------------------------------------------
def pulso():
    clock.value(1)
    time.sleep_us(500)
    clock.value(0)
    time.sleep_us(500)

# ---------------------------------------------------------
# Función que envía un número de 16 bits a la matriz
# Recorre cada bit y lo sincroniza con un pulso de reloj
# ----------------------------------------------------------
def enviar_16bits(valor):
    for i in range(16):
        bit = (valor >> (15 - i)) & 1   
        data.value(bit)                 
        pulso()                         

# --------------------------------
# Función apaga todos los LEDs.
# --------------------------------
def apagar():
    enviar_16bits(0)

# --------------------------------
# Diccionario que mapea letras/números a posiciones en la matriz
# Cada letra se representa con una columna y una fila
# --------------------------------
mapa = {
     # fila 1
    'A': (0, FILA1),
    'C': (1, FILA1),
    'E': (2, FILA1),
    'G': (3, FILA1),
    'I': (4, FILA1),
    'K': (5, FILA1),
    'M': (6, FILA1),
    'O': (7, FILA1),
    'Q': (8, FILA1),
    'S': (9, FILA1),
    'U': (10, FILA1),
    'W': (11, FILA1),
    'Y': (12, FILA1),

    # fila 2
    'B': (0, FILA2),
    'D': (1, FILA2),
    'F': (2, FILA2),
    'H': (3, FILA2),
    'J': (4, FILA2),
    'L': (5, FILA2),
    'N': (6, FILA2),
    'P': (7, FILA2),
    'R': (8, FILA2),
    'T': (9, FILA2),
    'V': (10, FILA2),
    'X': (11, FILA2),
    'Z': (12, FILA2),

    # fila 3
    '0': (0, FILA3),
    '1': (1, FILA3),
    '2': (2, FILA3),
    '3': (3, FILA3),
    '4': (4, FILA3),
    '5': (5, FILA3),
    '6': (6, FILA3),
    '7': (7, FILA3),
    '8': (8, FILA3),
    '9': (9, FILA3),
    '-': (10, FILA3),
    '+': (12, FILA3)
}

# ---------------------------------------------------------------------------------
# Función que muestra una letra en la matriz
# Busca la letra en el mapa y enciende la columna y la fila donde se encuentra
# ---------------------------------------------------------------------------------
def mostrar(letra):
    apagar()
    letra = letra.upper()
    if letra in mapa:
        columna, fila = mapa[letra]
        valor = 0
        valor |= (1 << columna)   # Enciende la columna
        valor |= (1 << fila)      # Enciende la fila
        enviar_16bits(valor)

# ---------------------------------------------------------------
# Función que muestra una palabra completa-
# Va letra por letra, con una pausa de 1 segundo entre cada una.}
# ---------------------------------------------------------------
def mostrar_palabra(texto):
    apagar()
    texto = texto.upper()
    for letra in texto:
        print("Mostrando:", letra)
        mostrar(letra)
        time.sleep(1)
        apagar()
    apagar()

# --------------------------------
# Diccionario Morse.
# --------------------------------
morse = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',    'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..',   'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',   'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-', 'R': '.-.',  'S': '...',  'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-',
    'Y': '-.--', 'Z': '--..',

    '0': '-----',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',

    ' ': '/',
    '+': '.-.-.',
    '-': '-....-'
}
morse_inv = {v:k for k,v in morse.items()}   # Diccionario se invierte para decodificar

# --------------------------------------------------------------------------
# Función que lee una letra en Morse usando el botón
# Si la pulsación es corta es un punto, si es larga entonces es raya
# Cuando hay una pausa larga, interpreta la secuencia y devuelve la letra
# -------------------------------------------------------------------------
def leer_letra():
    secuencia = ""
    while True:
        while boton.value() == 0:
            pass
        inicio = time.ticks_ms()
        buzzer.value(1)
        while boton.value() == 1:
            pass
        buzzer.value(0)
        duracion = (time.ticks_ms() - inicio) / 1000
        if duracion < UMBRAL:
            secuencia += '.'
            print(".", end="")
        else:
            secuencia += '-'
            print("-", end="")
        pausa_inicio = time.ticks_ms()
        while boton.value() == 0:
            pausa = (time.ticks_ms() - pausa_inicio) / 1000
            if pausa > UNIDAD * 3: 
                letra = morse_inv.get(secuencia, "?")
                print(" ->", letra)
                mostrar(letra)
                return letra
# --------------------------------
# MAIN
# --------------------------------

# apagar LEDs al iniciar
data.value(0)
clock.value(0)
time.sleep(0.1)
apagar()

print("Sistema StrangerTEC listo")

ultimo_estado = -1

while True:

    # --------------------------------
    # 1. Cambio del switch
    # --------------------------------
    estado_actual = switch_modo.value()

    if estado_actual != ultimo_estado:

        if estado_actual == 0:

            print("SWITCH_OFF")
            print("Modo LOCAL activo")

        else:

            print("SWITCH_ON")
            print("Modo VERSUS activo - Botón bloqueado")

        ultimo_estado = estado_actual

    # --------------------------------
    # 2. Revisar mensajes desde PC
    # --------------------------------
    msg_pc = leer_serial()

    if msg_pc:

        print("RECIBIDO:", msg_pc)

        mostrar_palabra(msg_pc)

    # --------------------------------
    # 3. Leer botón SOLO en modo LOCAL
    # --------------------------------
    if estado_actual == 0:

        if boton.value() == 1:

            letra = leer_letra()

            if letra != "?":

                sys.stdout.write(letra + "\n")

    time.sleep(0.01)