import pandas as pd
import random
import time
import pygame
import serial
from datetime import datetime

# Configuração da porta serial
porta_serial = 'COM7'  # Porta serial a ser lida
baud_rate = 115200  # Velocidade de comunicação
    
# Caminhos para os arquivos de áudio
conc_song = 'rotulagem2/musicas/conc-song.mp3'    # Música tocada durante o período de concentração
relax_song = 'rotulagem2/musicas/relax-song.mp3'  # Música tocada durante o período de relaxamento
start_conc = 'rotulagem2/musicas/start-conc.mp3'  # Alerta inicial para começar a concentração
end_conc = 'rotulagem2/musicas/end-conc.mp3'      # Alerta final para terminar a concentração

# Inicializa o pygame para tocar sons
pygame.mixer.init()
# pygame.mixer.music.set_volume(0.1)

# Cria um DataFrame vazio para armazenar os dados
df = pd.DataFrame(columns=['VALUE', 'TIMESTAMP', 'CONCENTRATION'])

def get_data(serial):
    """Obtém um valor de dados da porta serial."""
    # return random.uniform(0, 1)
    try:
        data = serial.readline().decode().strip()
        if data:
            return float(data)
            
    except Exception as e:
        print(f"Erro ao ler ou converter dados: {e}")
        serial.close()
        exit()
    
def log_data(measured_value, concentration):
    """Registra o valor medido e o estado de concentração no DataFrame."""
    global df
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame({'VALUE': [measured_value], 'TIMESTAMP': [timestamp], 'CONCENTRATION': [concentration]})
    df = pd.concat([df, new_row], ignore_index=True)
    print(f"{timestamp} | {measured_value:^8} | {concentration}")
   
def play_sound(file, loop=0):
    """Toca o arquivo de som especificado."""
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(loops=loop)

def main():
    global porta_serial, baud_rate ,conc_song, relax_song, start_conc, end_conc
    
    # Abre a porta serial
    ser = serial.Serial(porta_serial, baud_rate)
    print(f"Porta serial {porta_serial} aberta com sucesso.")
    
    try:
        while True:
            # Toca a música de relaxamento em loop
            play_sound(relax_song, -1)
            
            # Período de relaxamento
            start_time = time.time()
            relaxed_duration = random.randint(20, 90)
            while time.time() - start_time < relaxed_duration:
                measured_value = get_data(ser)
                log_data(measured_value, 0)
            
            # Toca o alerta para iniciar a concentração
            play_sound(start_conc)
            
            # Intervalo pré-concentração
            start_time = time.time()
            while time.time() - start_time < 3:
                measured_value = get_data(ser)
                log_data(measured_value, 0)
            
            # Período de concentração
            play_sound(conc_song, -1)
            start_time = time.time()
            concentrated_duration = random.randint(15, 40)
            print("Duração de concentração:", concentrated_duration)
            while time.time() - start_time < concentrated_duration:
                measured_value = get_data(ser)
                log_data(measured_value, 1)
            
            # Toca o alerta para terminar a concentração
            play_sound(end_conc)
            
            # Intervalo pós-concentração
            start_time = time.time()
            while time.time() - start_time < 5:
                measured_value = get_data(ser)
                log_data(measured_value, 1)

    except KeyboardInterrupt:
        print("Programa interrompido pelo usuário.")
    
    finally:
        # Salva o DataFrame em um arquivo CSV
        try:
            # file_name = f'bci_data_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
            file_name = 'bci_data.csv'
            df.to_csv(file_name, index=False, sep=';')
            print(f"Dados salvos em '{file_name}' - TOTAL {len(df)}.")
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

# Executa a função principal ao iniciar o script
if __name__ == "__main__":
    main()
