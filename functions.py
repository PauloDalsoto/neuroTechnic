import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy.fftpack import fft
import pywt
from scipy.interpolate import interp1d
import serial
import joblib 
from sklearn.ensemble import GradientBoostingClassifier

def get_data(serial_conn):
    """Obtém um valor de dados da porta serial."""
    try:
        if serial_conn.in_waiting > 0:
            data = serial_conn.readline().decode().strip()
            if data:
                return float(data)
    except Exception as e:
        print(f"Erro ao ler ou converter dados: {e}")
        serial_conn.close()
        exit()

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """Aplica filtro passa-baixa nos dados."""
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def pad_or_interpolate(array, target_length):
    """Preenche ou interpola array para um comprimento alvo."""
    if len(array) < target_length:
        return np.pad(array, (0, target_length - len(array)), 'constant', constant_values=0)
    elif len(array) > target_length:
        x = np.arange(len(array))
        f = interp1d(x, array, kind='linear', fill_value='extrapolate')
        x_new = np.linspace(0, len(array) - 1, target_length)
        return f(x_new)
    else:
        return array

def extract_wavelet_features(data, wavelet='db4'):
    """Extrai features usando a transformada wavelet."""
    coeffs = pywt.wavedec(data, wavelet)
    wavelet_features = []
    for coeff in coeffs:
        wavelet_features.extend([np.mean(coeff), np.var(coeff), np.min(coeff), np.max(coeff)])
    return wavelet_features

def process_window(window, cutoff, fixed_length):
    """Processa uma janela de dados, aplicando filtro e extraindo features."""
    values = window['VALUE'].values - np.mean(window['VALUE'].values)
    timestamp_diff = window['TIMESTAMP'].diff().dt.total_seconds()
    sampling_rate = 1 / timestamp_diff[timestamp_diff > 0].mean()

    fft_values = np.abs(fft(values))[:len(values) // 2]
    freqs = np.fft.fftfreq(len(values), d=1 / sampling_rate)[:len(values) // 2]
    fft_values_filtered = fft_values[freqs <= (cutoff + 5)]
    fft_values_filtered = pad_or_interpolate(fft_values_filtered, fixed_length)

    wavelet_features = extract_wavelet_features(values)

    features = list(fft_values_filtered) + list(wavelet_features)
    return features

def load_model(model_path):
    """Carrega o modelo Gradient Boosting."""
    model = joblib.load(model_path)
    return model

def classify_signal(model, features):
    """Classifica o sinal com base nas features extraídas."""
    prediction = model.predict([features])
    return prediction[0]