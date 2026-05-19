import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math
import plotly.graph_objects as go
import plotly.express as px

# Variable global para cache de datos procesados
_cache_datos_procesados = None

def cargar_datos_procesados():
    """Carga y procesa los datos del CSV una sola vez."""
    global _cache_datos_procesados
    
    if _cache_datos_procesados is not None:
        return _cache_datos_procesados
    
    # Carga desde la carpeta obligatoria data/
    df = pd.read_csv('data/players_stats_by_season_full_details.csv')
    
    # Filtrar solo datos de temporada regular y NBA
    df = df[(df['Stage'] == 'Regular_Season') & (df['League'] == 'NBA')].copy()
    
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
    
    # Convertir columnas numéricas
    columnas_numericas = ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']
    for col in columnas_numericas:
        df_tabla[col] = pd.to_numeric(df_tabla[col], errors='coerce').fillna(0)
    
    _cache_datos_procesados = {
        'df': df,
        'df_tabla': df_tabla,
        'df_original': df.copy()
    }
    
    return _cache_datos_procesados

def obtener_anos_unicos():
    """Obtiene los años únicos disponibles en los datos."""
    datos = cargar_datos_procesados()
    anos_unicos = sorted([int(ano) for ano in datos['df_tabla']['Año'].unique()], reverse=True)
    return anos_unicos

def obtener_datos_paginados(ano, pagina=1, items_por_pagina=20):
    """
    Obtiene datos paginados para un año específico.
    
    Args:
        ano (int): Año a filtrar
        pagina (int): Número de página (1-indexed)
        items_por_pagina (int): Cantidad de items por página
    
    Returns:
        dict: Con las claves 'datos', 'total_jugadores', 'pagina_actual', 'total_paginas'
    """
    datos = cargar_datos_procesados()
    df_tabla = datos['df_tabla']
    
    # Filtrar por año
    df_filtrado = df_tabla[df_tabla['Año'] == ano].copy()
    
    # Calcular totales
    total_jugadores = len(df_filtrado)
    total_paginas = math.ceil(total_jugadores / items_por_pagina) if total_jugadores > 0 else 1
    
    # Validar página
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas
    
    # Calcular índices
    inicio = (pagina - 1) * items_por_pagina
    fin = inicio + items_por_pagina
    
    # Obtener datos de la página (sin columnas Año y Temporada)
    df_pagina = df_filtrado[['Liga', 'Jugador', 'Equipo', 'Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']].iloc[inicio:fin]
    
    # Convertir a lista de diccionarios
    datos_lista = df_pagina.to_dict('records')
    
    # Convertir valores numéricos
    for fila in datos_lista:
        for col in ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']:
            if col in fila:
                fila[col] = float(fila[col])
    
    return {
        'datos': datos_lista,
        'total_jugadores': int(total_jugadores),
        'pagina_actual': pagina,
        'total_paginas': int(total_paginas)
    }

def procesar_y_graficar():
    # Carga desde la carpeta obligatoria data/
    df = pd.read_csv('data/players_stats_by_season_full_details.csv')
    
    # Filtrar solo datos de temporada regular
    df = df[df['Stage'] == 'Regular_Season'].copy()
    
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


# ============================================================================
# MÉTRICAS AVANZADAS
# ============================================================================

def calcular_metricas_avanzadas(ano):
    """
    Calcula métricas avanzadas para un año específico.
    
    Retorna:
        - Porcentaje de Tiro de Campo (TC%)
        - Porcentaje de Tiros de 2 puntos
        - Puntos por Partido (PPP) estimado
        - Volumen de tiro por partido
    """
    datos = cargar_datos_procesados()
    df_tabla = datos['df_tabla']
    
    # Filtrar por año
    df_filtrado = df_tabla[df_tabla['Año'] == ano].copy()
    
    # Convertir columnas a números
    for col in ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
    
    # Calcular métricas
    df_filtrado['TC%'] = (df_filtrado['Encestadas'] / df_filtrado['Canastas Tiradas']).replace([float('inf'), float('-inf')], 0) * 100
    df_filtrado['TC%'] = df_filtrado['TC%'].round(2)
    
    # Tiros de 2 puntos (canastas totales - triples)
    df_filtrado['Tiros 2P'] = df_filtrado['Encestadas'] - df_filtrado['3 Puntos']
    df_filtrado['2P%'] = (df_filtrado['Tiros 2P'] / (df_filtrado['Canastas Tiradas'] - df_filtrado['3 Puntos'])).replace([float('inf'), float('-inf')], 0) * 100
    df_filtrado['2P%'] = df_filtrado['2P%'].round(2)
    
    # Puntos por Partido (PPP) estimado: (Tiros 2P * 2 + 3 Puntos * 3) / Partidos Jugados
    df_filtrado['Puntos Estimados'] = (df_filtrado['Tiros 2P'] * 2) + (df_filtrado['3 Puntos'] * 3)
    df_filtrado['PPP'] = (df_filtrado['Puntos Estimados'] / df_filtrado['Partidos Jugados']).replace([float('inf'), float('-inf')], 0)
    df_filtrado['PPP'] = df_filtrado['PPP'].round(2)
    
    # Volumen de tiro por partido
    df_filtrado['Vol. Tiro/Partido'] = (df_filtrado['Canastas Tiradas'] / df_filtrado['Partidos Jugados']).replace([float('inf'), float('-inf')], 0)
    df_filtrado['Vol. Tiro/Partido'] = df_filtrado['Vol. Tiro/Partido'].round(2)
    
    # Seleccionar columnas relevantes
    columnas_resultado = [
        'Jugador', 'Equipo', 'Partidos Jugados', 
        'Canastas Tiradas', 'Encestadas', '3 Puntos',
        'TC%', '2P%', 'PPP', 'Vol. Tiro/Partido'
    ]
    
    df_resultado = df_filtrado[columnas_resultado].copy()
    df_resultado = df_resultado.sort_values('PPP', ascending=False)
    
    # Convertir a lista de diccionarios
    datos_lista = df_resultado.to_dict('records')
    
    # Convertir valores numéricos
    for fila in datos_lista:
        for col in fila:
            if isinstance(fila[col], float):
                fila[col] = round(fila[col], 2)
            elif isinstance(fila[col], int):
                fila[col] = int(fila[col])
    
    return datos_lista


def generar_scatter_plot(ano):
    """
    Genera un scatter plot interactivo: Canastas Tiradas vs Porcentaje de Acierto (TC%).
    Muestra quiénes son las "estrellas eficientes" y los "agujeros negros".
    Con hover interactivo que muestra estadísticas del jugador.
    """
    datos = cargar_datos_procesados()
    df_tabla = datos['df_tabla']
    
    # Filtrar por año
    df_filtrado = df_tabla[df_tabla['Año'] == ano].copy()
    
    # Convertir columnas a números
    for col in ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
    
    # Calcular TC%
    df_filtrado['TC%'] = (df_filtrado['Encestadas'] / df_filtrado['Canastas Tiradas']).replace([float('inf'), float('-inf')], 0) * 100
    
    # Calcular 2P%
    df_filtrado['Tiros 2P'] = df_filtrado['Encestadas'] - df_filtrado['3 Puntos']
    df_filtrado['2P%'] = (df_filtrado['Tiros 2P'] / (df_filtrado['Canastas Tiradas'] - df_filtrado['3 Puntos'])).replace([float('inf'), float('-inf')], 0) * 100
    
    # Calcular PPP
    df_filtrado['Puntos Estimados'] = (df_filtrado['Tiros 2P'] * 2) + (df_filtrado['3 Puntos'] * 3)
    df_filtrado['PPP'] = (df_filtrado['Puntos Estimados'] / df_filtrado['Partidos Jugados']).replace([float('inf'), float('-inf')], 0)
    
    # Filtrar solo jugadores que han tirado más de 0 canastas
    df_filtrado = df_filtrado[df_filtrado['Canastas Tiradas'] > 0]
    
    # Asignar colores por equipo
    equipos_unicos = df_filtrado['Equipo'].unique()
    colores_equipos = px.colors.qualitative.Light24 * 10  # Repetir colores si hay más de 24 equipos
    color_map = {equipo: colores_equipos[i % len(colores_equipos)] for i, equipo in enumerate(equipos_unicos)}
    df_filtrado['Color'] = df_filtrado['Equipo'].map(color_map)
    
    # Crear scatter plot interactivo con Plotly
    fig = go.Figure()
    
    # Agregar puntos de jugadores
    fig.add_trace(go.Scatter(
        x=df_filtrado['Canastas Tiradas'],
        y=df_filtrado['TC%'],
        mode='markers',
        marker=dict(
            size=8,
            color=df_filtrado['Color'],
            line=dict(width=1, color='rgba(0,0,0,0.3)'),
            opacity=0.7
        ),
        text=[
            f"<b>{row['Jugador']}</b><br>" +
            f"Equipo: {row['Equipo']}<br>" +
            f"Partidos: {int(row['Partidos Jugados'])}<br>" +
            f"Canastas Tiradas: {int(row['Canastas Tiradas'])}<br>" +
            f"Encestadas: {int(row['Encestadas'])}<br>" +
            f"3 Puntos: {int(row['3 Puntos'])}<br>" +
            f"TC%: {row['TC%']:.2f}%<br>" +
            f"2P%: {row['2P%']:.2f}%<br>" +
            f"PPP: {row['PPP']:.2f}"
            for idx, row in df_filtrado.iterrows()
        ],
        hovertemplate='%{text}<extra></extra>',
        name='Jugadores'
    ))
    
    # Calcular promedio y mediana para líneas de referencia
    promedio_tc = df_filtrado['TC%'].mean()
    mediana_ct = df_filtrado['Canastas Tiradas'].median()
    
    # Agregar línea de referencia horizontal (promedio TC%)
    fig.add_hline(
        y=promedio_tc,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Promedio TC%: {promedio_tc:.1f}%",
        annotation_position="right"
    )
    
    # Agregar línea de referencia vertical (mediana CT)
    fig.add_vline(
        x=mediana_ct,
        line_dash="dash",
        line_color="#f97316",
        annotation_text=f"Mediana: {mediana_ct:.0f}",
        annotation_position="top"
    )
    
    # Actualizar layout
    fig.update_layout(
        title=f'Eficiencia de Tiro: Volumen vs Porcentaje - Año {ano}',
        xaxis_title='Canastas Tiradas',
        yaxis_title='Porcentaje de Acierto (TC%)',
        hovermode='closest',
        height=700,
        template='plotly_white',
        showlegend=False,
        font=dict(size=11),
        xaxis=dict(gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(gridwidth=1, gridcolor='lightgray')
    )
    
    # Guardar gráfico HTML
    ruta_grafico = 'src/static/img/scatter_eficiencia.html'
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    fig.write_html(ruta_grafico)
    
    return 'static/img/scatter_eficiencia.html'


def generar_grafico_equipos(ano):
    """
    Genera un gráfico de barras que compara el rendimiento total de los equipos.
    Suma las estadísticas de todos los jugadores por equipo.
    """
    datos = cargar_datos_procesados()
    df_tabla = datos['df_tabla']
    
    # Filtrar por año
    df_filtrado = df_tabla[df_tabla['Año'] == ano].copy()
    
    # Convertir columnas a números
    for col in ['Partidos Jugados', 'Canastas Tiradas', 'Encestadas', '3 Puntos']:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
    
    # Agrupar por equipo y sumar
    df_equipos = df_filtrado.groupby('Equipo').agg({
        'Encestadas': 'sum',
        '3 Puntos': 'sum',
        'Canastas Tiradas': 'sum'
    }).reset_index()
    
    # Calcular puntos totales estimados
    df_equipos['Tiros 2P'] = df_equipos['Encestadas'] - df_equipos['3 Puntos']
    df_equipos['Puntos Totales'] = (df_equipos['Tiros 2P'] * 2) + (df_equipos['3 Puntos'] * 3)
    
    # Ordenar por puntos totales
    df_equipos = df_equipos.sort_values('Puntos Totales', ascending=True).tail(20)
    
    # Crear gráfico de barras horizontal
    plt.figure(figsize=(14, 10))
    
    bars = plt.barh(df_equipos['Equipo'], df_equipos['Puntos Totales'], color='#f97316', edgecolor='black', linewidth=0.7)
    
    # Colorear barras con gradiente
    colors = plt.cm.Oranges(df_equipos['Puntos Totales'] / df_equipos['Puntos Totales'].max())
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    plt.xlabel('Puntos Totales Estimados', fontsize=12, fontweight='bold')
    plt.title(f'Rendimiento Ofensivo por Equipo - Año {ano}', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (equipo, puntos) in enumerate(zip(df_equipos['Equipo'], df_equipos['Puntos Totales'])):
        plt.text(puntos + 50, i, f'{int(puntos)}', va='center', fontsize=9)
    
    plt.tight_layout()
    
    # Guardar gráfico
    ruta_grafico = 'src/static/img/barras_equipos.png'
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico, dpi=100, bbox_inches='tight')
    plt.close()
    
    return 'static/img/barras_equipos.png'
