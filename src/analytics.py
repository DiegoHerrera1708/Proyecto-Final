import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math

def procesar_y_graficar():
    # Carga desde la carpeta obligatoria data/
    df = pd.read_csv('data/players_stats_by_season_full_details.csv')
    
    
    # Seleccionar solo las columnas solicitadas
    columnas_mostrar = ['League', 'Season', 'Player', 'Team', 'GP', 'FGA', 'FGM', '3PM']
    df_tabla = df[columnas_mostrar].copy()
    
    # Limpiar datos nulos
    df_tabla = df_tabla.fillna(0)
    
    # Extraer el año de la columna Season (ej: "1999 - 2000" -> 1999)
    df_tabla['Año'] = df_tabla['Season'].str.extract(r'(\d{4})').astype(int)
    
    # Renombrar columnas para mejor presentación
    df_tabla.columns = ['Liga', 'Temporada', 'Jugador', 'Equipo', 'Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos', 'Año']
    
    # Ordenar por año descendente
    df_tabla = df_tabla.sort_values(['Año', 'Liga'], ascending=[False, True])
    
    # Gráfico 1: Rendimiento por Jugador (Top 10 general)
    top_players = df.nlargest(10, 'PTS')[['Player', 'PTS']].reset_index(drop=True)
    plt.figure(figsize=(12, 6))
    colors = plt.cm.viridis(range(len(top_players)))
    plt.barh(range(len(top_players)), top_players['PTS'].values, color=colors)
    plt.yticks(range(len(top_players)), top_players['Player'].values)
    plt.title('Top 10 Jugadores por Puntos Totales')
    plt.xlabel('Puntos')
    plt.tight_layout()
    
    # Guardar en static para la web
    ruta_grafico = 'src/static/img/goles_player.png'
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico)
    plt.close()
    
    # Obtener años y ligas únicas ordenadas
    anos_unicos = sorted([int(ano) for ano in df_tabla['Año'].unique()], reverse=True)
    
    # Crear diccionario con datos por liga y año
    datos_por_filtro = {}
    for liga in df_tabla['Liga'].unique():
        datos_por_filtro[liga] = {}
        for ano in anos_unicos:
            df_filtro = df_tabla[(df_tabla['Liga'] == liga) & (df_tabla['Año'] == ano)].copy()
            # Removemos las columnas Año y Temporada del dataframe para la tabla (mantener Liga)
            df_filtro_tabla = df_filtro.drop(columns=['Año', 'Temporada'])
            
            # Convertir columnas numéricas a float/int para asegurar compatibilidad con JSON
            columnas_numericas = ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']
            for col in columnas_numericas:
                df_filtro_tabla[col] = pd.to_numeric(df_filtro_tabla[col], errors='coerce').fillna(0)
            
            # Convertir a lista de diccionarios para pasarla a JavaScript
            datos_lista = df_filtro_tabla.to_dict('records')
            
            # Convertir valores numéricos en la lista de diccionarios
            for fila in datos_lista:
                for col in columnas_numericas:
                    if col in fila:
                        fila[col] = float(fila[col])
            
            datos_por_filtro[liga][int(ano)] = {
                'datos': datos_lista,
                'total_jugadores': len(datos_lista),
                'total_paginas': math.ceil(len(datos_lista) / 20)
            }
    
    return datos_por_filtro, anos_unicos