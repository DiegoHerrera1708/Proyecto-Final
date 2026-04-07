from flask import Flask, render_template
import os
# from models import Jugador 
from analytics import procesar_y_graficar

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', titulo="Gestión Deportiva")

@app.route('/dashboard')
def dashboard():
    try:
        # 1. Llamamos a la función de analítica que procesa el CSV en data/
        # y genera los gráficos en static/img/
        tabla_html = procesar_y_graficar()
        
        # 2. Renderizamos el template pasando la tabla generada por Pandas
        return render_template('dashboard.html', tabla_html=tabla_html)
    
    except FileNotFoundError:
        # Gestión de errores  
        return "Error: No se encontró el archivo de datos en la carpeta data/", 404
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}", 500

if __name__ == '__main__':
    # Punto de entrada de la aplicación 
    app.run(debug=True)