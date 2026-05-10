import utime

from machine import Pin

buzzer = Pin(14, Pin.OUT)

while True:

  buzzer.high() #Enciende el buzzer

  utime.sleep(1) # el tiempo en que se mantiene encendido

  buzzer.low() #Se apaga

  utime.sleep(1) #Tiempo en que se mantiene apagado