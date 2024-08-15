def get_data(serial):
        """Obtém um valor de dados da porta serial."""
    # return random.uniform(0, 1)
    try:
        if serial.in_waiting > 0:
            data = serial.readline().decode().strip()
            if data:
                return float(data)
            
    except Exception as e:
        print(f"Erro ao ler ou converter dados: {e}")
        serial.close()
        exit()

def overlap_windows():
    pass

def filter_data():
    pass

def fourier_transform():
    pass

def classify_data():
    pass

def check_classification():
    pass

