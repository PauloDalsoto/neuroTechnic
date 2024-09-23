import serial
import keyboard
import time

# Configurações da porta serial (modifique a porta para a porta correta do Arduino)
ser = serial.Serial('COM10', 9600)
time.sleep(2)  # Esperar a conexão estabilizar

# Variável para armazenar o estado do relé
rele_ligado = False

def alternar_rele():
    global rele_ligado
    if rele_ligado:
        ser.write(b'OFF\n')  # Envia comando para desligar o relé
        rele_ligado = False
    else:
        ser.write(b'ON\n')  # Envia comando para ligar o relé
        print("Ligando relé")
        rele_ligado = True

# Detecta a tecla espaço
while True:
    for i in range(10):
        time.sleep(1)
        print("Relé Desligado")
    alternar_rele()
    for i in range(12):
        time.sleep(1)

    # try:
    #     if keyboard.is_pressed('space'):
    #         alternar_rele()
    #         time.sleep(0.5)  # Pequena pausa para evitar múltiplas detecções rápidas
    # except KeyboardInterrupt:
    #     print("Encerrando programa...")
    #     break

ser.close()  # Fecha a conexão serial quando o programa é encerrado
