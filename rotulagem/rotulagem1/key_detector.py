import serial
import pandas as pd
import keyboard
from datetime import datetime
import time

# Configuração da porta serial
porta_serial = 'COM7'  # Porta serial a ser lida
baud_rate = 115200  # Velocidade de comunicação

# Inicializa o DataFrame vazio
df = pd.DataFrame(columns=['TIMESTAMP', 'VALUE', 'PRESS'])

try:
    # Abre a porta serial
    ser = serial.Serial(porta_serial, baud_rate)
    print(f"Porta serial {porta_serial} aberta com sucesso.")

    # Loop para leitura contínua
    while True:
        # Verifica se há dados disponíveis para leitura
        if ser.in_waiting > 0:
            # Lê os dados da porta serial
            dados = ser.readline().decode().strip()
            print(f"Dado recebido: {dados}")
            
            # Verifica se a tecla de espaço está pressionada
            if keyboard.is_pressed('space'):
                press = 1
            else:
                press = 0
            
            # Cria um novo DataFrame com os dados atuais
            new_data = pd.DataFrame({'TIMESTAMP': [datetime.now()], 'VALUE': [dados], 'PRESS': [press]})
            
            # Concatena o novo DataFrame com o DataFrame existente
            df = pd.concat([df, new_data], ignore_index=True)

        # Verifica se a tecla ESC foi pressionada para finalizar o programa
        if keyboard.is_pressed('esc'):
            # Salva o DataFrame em um arquivo CSV
            df.to_csv('dados_coletados.csv', index=False)
            print("Dados coletados salvos.")
            break

except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial {porta_serial}: {e}")

finally:
    # Fecha a porta serial ao sair do programa
    try:
        if ser.is_open:
            ser.close()
            print(f"Porta serial {porta_serial} fechada.")
    except NameError:
        pass
