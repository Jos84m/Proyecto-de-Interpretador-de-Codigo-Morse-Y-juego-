import serial
import time

puerto = serial.Serial('COM4', 115200)
time.sleep(2)

def enviar_frase(frase):
    puerto.write((frase + "\n").encode())