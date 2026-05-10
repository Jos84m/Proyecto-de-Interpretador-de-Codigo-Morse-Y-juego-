from machine import Pin
import time

#Prueba del dip swhitch
switch_local = Pin(17, Pin.IN, Pin.PULL_DOWN)
switch_versus = Pin(16, Pin.IN, Pin.PULL_DOWN)

while True:
    estado_local = switch_local.value()
    estado_versus = switch_versus.value()
    
    if estado_local == 1:
        print("Switch 1 (LOCAL): ACTIVADO")
    
    if estado_versus == 1:
        print("Switch 2 (VERSUS): ACTIVADO")
        
    if estado_local == 0 and estado_versus == 0:
        print("Esperando... (Todos en OFF)")
        
    time.sleep(0.5)