import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def adicionar_milissegundos(df):
    """
    Adiciona milissegundos aos timestamps para registros com o mesmo timestamp,
    distribuindo milissegundos de forma crescente dentro de cada segundo.
    
    Parameters:
    df (pd.DataFrame): DataFrame com colunas 'VALUE', 'TIMESTAMP', 'CONCENTRATION'.
    
    Returns:
    pd.DataFrame: DataFrame com timestamps ajustados.
    """
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    
    # Ordenar o DataFrame por índice para preservar a ordem original
    df = df.sort_index()
    
    # Agrupar por segundo
    df['SECOND'] = df['TIMESTAMP'].dt.floor('S')
    
    novos_timestamps = []
    
    for _, grupo in df.groupby('SECOND'):
        contagem = len(grupo)
        
        # Gerar milissegundos crescentes com 3 casas decimais
        milissegundos = np.linspace(0, 999, contagem)
        
        for i, (_, linha) in enumerate(grupo.iterrows()):
            milissegundos_ajustados = round(milissegundos[i], 3)
            novo_timestamp = linha['SECOND'] + timedelta(milliseconds=milissegundos_ajustados)
            novos_timestamps.append((linha.name, novo_timestamp))
    
    # Ordenar pelos índices originais para preservar a ordem
    novos_timestamps = sorted(novos_timestamps, key=lambda x: x[0])
    
    df['TIMESTAMP'] = [ts for _, ts in novos_timestamps]
    df = df.drop(columns=['SECOND'])  # Remover a coluna SECOND

    # Formatar os timestamps para ter exatamente 3 casas decimais
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S.') + df['TIMESTAMP'].dt.strftime('%f').str[:3]
    
    return df


# Ler o CSV
input_file = 'data/bci_data_correto5.csv'
output_file = 'aa.csv'


df = pd.read_csv(input_file, delimiter=';')

# Ajustar timestamps
df_ajustado = adicionar_milissegundos(df)

# Salvar o CSV ajustado
df_ajustado.to_csv(output_file, index=False, sep=';')

print(f"Arquivo ajustado salvo em {output_file}")
