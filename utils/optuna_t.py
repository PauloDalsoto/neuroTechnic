import glob
import os
import json
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy.fftpack import fft
import pywt
from scipy.interpolate import interp1d
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
import optuna

# Função de pré-processamento e extração de características
def preprocess_and_extract_features(csv_files, window_size, overlap, cutoff, frequencia_amostragem, fixed_length, features_to_use):
    X_features = []
    y_labels = []

    def pad_or_interpolate(array, target_length):
        if len(array) < target_length:
            return np.pad(array, (0, target_length - len(array)), 'constant', constant_values=0)
        elif len(array) > target_length:
            x = np.arange(len(array))
            f = interp1d(x, array, kind='linear', fill_value='extrapolate')
            x_new = np.linspace(0, len(array)-1, target_length)
            return f(x_new)
        else:
            return array

    def butter_lowpass_filter(data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    def band_power_fft(fft_values, freqs, band):
        band_power = np.trapezoid(fft_values[(freqs >= band[0]) & (freqs <= band[1])], freqs[(freqs >= band[0]) & (freqs <= band[1])])
        return band_power

    def extract_stat_features(data):
        mean = np.mean(data)
        variance = np.var(data)
        skewness = pd.Series(data).skew()
        kurtosis = pd.Series(data).kurtosis()
        return mean, variance, skewness, kurtosis

    def extract_wavelet_features(data, wavelet='db4'):
        coeffs = pywt.wavedec(data, wavelet)
        wavelet_features = []
        for coeff in coeffs:
            wavelet_features.extend([np.mean(coeff), np.var(coeff), np.min(coeff), np.max(coeff)])
        return wavelet_features

    for file in csv_files:
        data = pd.read_csv(file, sep=';')
        data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
        data['VALUE'] = data['VALUE'] * (3.3 / 4098)
        # print(f'Processando arquivo {file} | {data.shape[0]:,} amostras')

        step_size = int(window_size * (1 - overlap))
        windows = []
        labels = []

        for start in range(0, len(data) - window_size + 1, step_size):
            end = start + window_size
            window = data.iloc[start:end]

            if window['CONCENTRATION'].any() == 1:
                labels.append(1)
            else:
                labels.append(0)

            windows.append(window)

        y_labels.extend(labels)

        f_windows = []
        for i, window in enumerate(windows):
            timestamp = np.array(window['TIMESTAMP'])
            value = np.array(window['VALUE'])
            filtered_value = butter_lowpass_filter(value, cutoff, frequencia_amostragem)
            filtered_window = pd.DataFrame({'TIMESTAMP': timestamp, 'VALUE': filtered_value})
            f_windows.append(filtered_window)

        for window in f_windows:
            values = window['VALUE'].values - np.mean(window['VALUE'].values)
            timestamp_diff = window['TIMESTAMP'].diff().dt.total_seconds()
            sampling_rate = 1 / timestamp_diff[timestamp_diff > 0].mean()

            fft_values = np.abs(fft(values))[:len(values)//2]
            freqs = np.fft.fftfreq(len(values), d=1/sampling_rate)[:len(values)//2]
            fft_values_filtered = fft_values[freqs <= (cutoff + 5)]
            
            fft_values_filtered = pad_or_interpolate(fft_values_filtered, fixed_length)
            
            features = []
            if 'fft' in features_to_use:
                features.extend(list(fft_values_filtered))
            if 'band_power' in features_to_use:
                delta_power = band_power_fft(fft_values, freqs, [0.5, 4])
                theta_power = band_power_fft(fft_values, freqs, [4, 8])
                alpha_power = band_power_fft(fft_values, freqs, [8, 13])
                beta_power = band_power_fft(fft_values, freqs, [13, 30])
                features.extend([delta_power, theta_power, alpha_power, beta_power])
            if 'stat' in features_to_use:
                mean, variance, skewness, kurtosis = extract_stat_features(values)
                features.extend([mean, variance, skewness, kurtosis])
            if 'wavelet' in features_to_use:
                wavelet_features = extract_wavelet_features(values)
                features.extend(wavelet_features)

            X_features.append(features)

    X_features = np.array(X_features)
    y_labels = np.array(y_labels)
    return X_features, y_labels

def get_csv():
    # Procurar arquivos CSV no diretório especificado
    csv_files = glob.glob('../data/*.csv')

    # Normalizar os caminhos dos arquivos para usar barras '/'
    csv_files = [os.path.normpath(file).replace('\\', '/') for file in csv_files]

    return csv_files
    
def log_results(model_name, f1_score, accuracy_score, precision_score, recall_score, params, filename='log.json'):
    log_entry = {
        'Model': model_name,
        'F1': f1_score,
        'Accuracy': accuracy_score,
        'Precision': precision_score,
        'Recall': recall_score,
        'Parameters': params
    }
    
    with open(filename, 'a') as file:
        file.write(json.dumps(log_entry) + '\n')


# Função objetivo do Optuna
def objective(trial):
    window_size = trial.suggest_int('window_size', 200, 3000)
    overlap = round(trial.suggest_float('overlap', 0.10, 0.60), 2)
    cutoff = trial.suggest_int('cutoff', 10, 60)
    fixed_length = trial.suggest_int('fixed_length', 50, 500)
    frequencia_amostragem = 250
    
    features_to_use = []
    if trial.suggest_categorical('use_fft', [True, False]):
        features_to_use.append('fft')
    if trial.suggest_categorical('use_band_power', [True, False]):
        features_to_use.append('band_power')
    if trial.suggest_categorical('use_stat', [True, False]):
        features_to_use.append('stat')
    if trial.suggest_categorical('use_wavelet', [True, False]):
        features_to_use.append('wavelet')
    
    csv_files = get_csv()
    X_features, y_labels = preprocess_and_extract_features(csv_files, window_size, overlap, cutoff, frequencia_amostragem, fixed_length, features_to_use)

    X_train, X_test, y_train, y_test = train_test_split(X_features, y_labels, test_size=0.3, random_state=74)

    classifiers = {
        'LinearSVC': LinearSVC(),
        'Logistic Regression': LogisticRegression(),
        'Random Forest': RandomForestClassifier(),
        'K-Nearest Neighbors': KNeighborsClassifier(),
        'Gradient Boosting': GradientBoostingClassifier(),
        'Decision Tree': DecisionTreeClassifier(),
        'Gaussian Naive Bayes': GaussianNB(),
        'Support Vector Classifier': SVC(),
        'AdaBoost Classifier': AdaBoostClassifier(),
        'Linear Discriminant Analysis': LinearDiscriminantAnalysis(),
        'MLP Classifier': MLPClassifier(hidden_layer_sizes=(24, 8, 6, 4), max_iter=1000, early_stopping=True)
    }

    best_f1 = 0
    for name, clf in classifiers.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        f1 = f1_score(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_accuracy = accuracy
            best_precision = precision
            best_recall = recall

     # Log the results
    log_results(best_model_name, best_f1, best_accuracy, best_precision, best_recall, trial.params)

    return best_f1

###############################################################################################################

# Executando a otimização
N_TESTES = 10000
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=N_TESTES)
