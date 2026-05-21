from flask import Flask, render_template, jsonify, request
import os
from analytics import (
    procesar_y_graficar, 
    obtener_datos_paginados, 
    obtener_anos_unicos,
    calcular_metricas_avanzadas,
    generar_scatter_plot,
    generar_grafico_equipos
)

app = Flask(__name__, static_folder='templates/static', static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html', titulo="Gestión Deportiva")

@app.route('/dashboard')
def dashboard():
    try:
        # Obtener años disponibles
        anos_unicos = obtener_anos_unicos()
        
        # Renderizar el template con los años disponibles
        return render_template('dashboard.html', 
                                anos_unicos=anos_unicos,
                                ano_inicial=anos_unicos[0] if anos_unicos else None)
    
    except FileNotFoundError:
        return "Error: No se encontró el archivo de datos en la carpeta data/", 404
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}", 500

@app.route('/api/datos-jugadores', methods=['GET'])
def api_datos_jugadores():
    """
    Endpoint API para obtener datos de jugadores con paginación.
    Parámetros:
        - ano: Año a filtrar (requerido)
        - pagina: Número de página (opcional, default=1)
        - items_por_pagina: Cantidad de items por página (opcional, default=20)
    """
    try:
        # Obtener parámetros
        ano = request.args.get('ano', type=int)
        pagina = request.args.get('pagina', default=1, type=int)
        items_por_pagina = request.args.get('items_por_pagina', default=20, type=int)
        
        # Validar parámetros
        if ano is None:
            return jsonify({'error': 'Parámetro "ano" es requerido'}), 400
        
        if pagina < 1:
            pagina = 1
        
        if items_por_pagina < 1 or items_por_pagina > 100:
            items_por_pagina = 20
        
        # Obtener datos
        resultado = obtener_datos_paginados(ano, pagina, items_por_pagina)
        
        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metricas-avanzadas', methods=['GET'])
def api_metricas_avanzadas():
    """
    Endpoint API para obtener métricas avanzadas de un año específico.
    Parámetros:
        - ano: Año a filtrar (requerido)
        - pagina: Número de página (opcional, default=1)
        - items_por_pagina: Cantidad de items por página (opcional, default=20)
    """
    try:
        # Obtener parámetros
        ano = request.args.get('ano', type=int)
        pagina = request.args.get('pagina', default=1, type=int)
        items_por_pagina = request.args.get('items_por_pagina', default=50, type=int)
        
        # Validar parámetros
        if ano is None:
            return jsonify({'error': 'Parámetro "ano" es requerido'}), 400
        
        if pagina < 1:
            pagina = 1
        
        if items_por_pagina < 1 or items_por_pagina > 200:
            items_por_pagina = 50
        
        # Obtener métricas
        metricas = calcular_metricas_avanzadas(ano)
        
        # Aplicar paginación
        total_jugadores = len(metricas)
        total_paginas = (total_jugadores + items_por_pagina - 1) // items_por_pagina
        
        if pagina > total_paginas and total_paginas > 0:
            pagina = total_paginas
        
        inicio = (pagina - 1) * items_por_pagina
        fin = inicio + items_por_pagina
        
        return jsonify({
            'datos': metricas[inicio:fin],
            'total_jugadores': total_jugadores,
            'pagina_actual': pagina,
            'total_paginas': total_paginas
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generar-graficos', methods=['GET'])
def api_generar_graficos():
    """
    Endpoint API para generar gráficos.
    Parámetros:
        - ano: Año a filtrar (requerido)
    """
    try:
        # Obtener parámetro
        ano = request.args.get('ano', type=int)
        
        # Validar parámetro
        if ano is None:
            return jsonify({'error': 'Parámetro "ano" es requerido'}), 400
        
        # Generar gráficos
        scatter_path = generar_scatter_plot(ano)
        barras_path = generar_grafico_equipos(ano)
        
        return jsonify({
            'scatter_plot': scatter_path,
            'grafico_equipos': barras_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)