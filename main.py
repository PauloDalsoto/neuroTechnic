from functions import *
import random
import time

# Parâmetros
window_size = 2952           # Número de amostras por janela
overlap = 0.57               # Sobreposição entre janelas
cutoff = 51                  # Frequência de corte em Hz
frequencia_amostragem = 250  # Taxa de amostragem média em Hz (ajustada para EEG típico)
fixed_length = 348           # Comprimento fixo para interpolação dos dados de FFT

def main(serial_conn, model_path):
    """Função principal para leitura de dados e processamento."""
    data_window = []
    model = load_model(model_path)

    while True:
        # data = get_data(serial_conn)
        data = random.uniform(0, 1)
        print(f"Valor medido: ", data)
        if data is not None:
            timestamp = pd.Timestamp.now()
            data_window.append({'TIMESTAMP': timestamp, 'VALUE': data})
            
            if len(data_window) >= window_size:
                df_window = pd.DataFrame(data_window)
                df_window['VALUE'] = butter_lowpass_filter(df_window['VALUE'], cutoff, frequencia_amostragem)
                
                features = process_window(df_window, cutoff, fixed_length)
                
                prediction = classify_signal(model, features)
                if prediction == 1:  
                    print("Concentração detectada!")
                    time.sleep(5)
                else:
                    print("...")

                # Descartar dados para próxima janela
                overlap_size = int(window_size * overlap)
                data_window = data_window[overlap_size:]

# Executa a função principal ao iniciar o script
if __name__ == "__main__":
    porta_serial = 'COM7'                         # Porta serial
    baud_rate = 115200                            # Velocidade de comunicação
    model_path = './utils/GB_mlp.pkl'    # Caminho do modelo

    # serial_conn = serial.Serial(porta_serial, baud_rate)
    serial_conn = 1
    main(serial_conn, model_path)