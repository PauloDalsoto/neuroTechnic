from functions import *
import random
import time

# Parâmetros
window_size = 2952           # Número de amostras por janela
overlap = 0.57               # Sobreposição entre janelas
cutoff = 51                  # Frequência de corte em Hz
frequencia_amostragem = 250  # Taxa de amostragem média em Hz (ajustada para EEG típico)
fixed_length = 348           # Comprimento fixo para interpolação dos dados de FFT

def main(serial_esp32, serial_uno, model_path):
    """Função principal para leitura de dados e processamento."""
    data_window = []
    model = load_model(model_path)

    print("Iniciando leitura de dados...")
    while True:
        data = get_data(serial_esp32)
        
        # print(f"Valor medido: ", data)
        if data is not None: 
            timestamp = pd.Timestamp.now()
            data_window.append({'TIMESTAMP': timestamp, 'VALUE': data})
            
            if len(data_window) >= window_size:
                df_window = pd.DataFrame(data_window)
                
                value = np.array(df_window['VALUE'])
                df_window['VALUE'] = butter_lowpass_filter(value, cutoff, frequencia_amostragem)
                
                features = process_window(df_window, cutoff, fixed_length, False)
                
                prediction = classify_signal(model, features)
                if prediction == 1:  
                    print("Concentração detectada!")
                    # serial_uno.write(b'ON\n') 
                    # time.sleep(5)
                else:
                    print("...")

                # Descartar dados para próxima janela
                data_window.clear()

# Executa a função principal ao iniciar o script
if __name__ == "__main__":
    model_path = './utils/mlp_without_fftFilter.pkl'   
    # model_path = './utils/GB_mlp.pkl'   

    serial_esp32 = serial.Serial('COM7', 115200)
    # serial_uno = serial.Serial('COM10', 9600) 
    serial_uno = 2
    time.sleep(3)
    print("Conexões estabelecidas!")
    
    main(serial_esp32, serial_uno, model_path)