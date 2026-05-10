from machine import Pin
import time

# ------------------------
# PINES
# ------------------------
data = Pin(1, Pin.OUT)    # Pin que envía los datos
clock = Pin(0, Pin.OUT)   # Pin que marca el ritmo (reloj)

boton = Pin(14, Pin.IN, Pin.PULL_DOWN) 
buzzer = Pin(15, Pin.OUT)               

# ------------------------
# CLOCK
# ------------------------
def pulso():
    # Esto indica al receptor cuándo debe leer el dato
    clock.value(1)
    time.sleep(0.001)
    clock.value(0)

# ------------------------
# ENVIAR 16 BITS
# ------------------------
def enviar_16bits(valor):
    for i in range(16):
        bit = (valor >> (15 - i)) & 1   # Se obtiene cada bit del número
        data.value(bit)                
        pulso()
        
# ------------------------
# MAIN
# ------------------------
contador = 0

while True:
# controla el buzzer y los LEDs según el botón
    # si presiona botón
    if boton.value():

        buzzer.value(1)
        valor = 1 << contador

        enviar_16bits(valor)

        contador += 1

        if contador >= 16:
            contador = 0

        while boton.value():
            pass

        time.sleep(0.1)

    else:

        buzzer.value(0)