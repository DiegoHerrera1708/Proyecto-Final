import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def procesar_y_graficar():
    # Carga desde la carpeta obligatoria data/ [cite: 34]
    df = pd.read_csv('data/partidos_originales.csv')
    
    # Limpieza Técnica (Requisito RA M4) [cite: 26, 41]
    df['goles'] = df['goles'].fillna(0)
    df['valoracion'] = df['valoracion'].fillna(df['valoracion'].mean())
    
    # Gráfico 1: Rendimiento por Jugador
    plt.figure(figsize=(10, 6))
    sns.barplot(x='jugador', y='goles', data=df, palette='viridis')
    plt.title('Goles Totales por Jugador')
    
    # Guardar en static para la web
    ruta_grafico = 'src/static/img/goles_player.png'
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico)
    plt.close()
    
    return df.to_html(classes='table table-striped') # Retorna la tabla para el Dashboard