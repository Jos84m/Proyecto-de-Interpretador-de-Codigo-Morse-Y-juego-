from machine import Pinfrom machine import Pin
import time

# Pines de salida: uno para datos y otro para reloj
data = Pin(1, Pin.OUT)
clock = Pin(0, Pin.OUT)

# Esta función hace un pulso de reloj (sube y baja rápido el pin clock)
# Sirve para marcar el ritmo y que el receptor sepa cuándo leer el dato
def pulso():
    clock.value(1)
    time.sleep(0.001)
    clock.value(0)

# Envía un número de 16 bits, uno por uno
def enviar_16bits(valor):
    for i in range(16):
        bit = (valor >> (15 - i)) & 1   # Se obtiene cada bit
        data.value(bit)
        pulso()   # Se sincroniza cada bit con un pulso

# Va encendiendo un bit diferente en cada vuelta
while True:
    for i in range(16):
        valor = 1 << i   # Solo un bit se enciende
        enviar_16bits(valor)
        time.sleep(0.12)
