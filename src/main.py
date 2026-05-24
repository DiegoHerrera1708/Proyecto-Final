from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import os
from datetime import datetime
from database import db, login_manager
from models import Usuario, EstadisticasPartido
from analytics import (
    procesar_y_graficar, 
    obtener_datos_paginados, 
    obtener_anos_unicos,
    calcular_metricas_avanzadas,
    generar_scatter_plot,
    generar_grafico_equipos
)

app = Flask(__name__, static_folder='templates/static', static_url_path='/static')
app.config['SECRET_KEY'] = 'tu-clave-secreta-super-segura-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear tablas
with app.app_context():
    db.create_all()

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

# ============ RUTAS DE AUTENTICACIÓN ============

@app.route('/api/registrarse', methods=['POST'])
def registrarse():
    """Endpoint para registrar un nuevo usuario"""
    try:
        datos = request.get_json()
        nombre = datos.get('nombre', '').strip()
        email = datos.get('email', '').strip()
        password = datos.get('password', '')
        confirmar_password = datos.get('confirmar_password', '')
        
        # Validaciones
        if not all([nombre, email, password, confirmar_password]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        if len(nombre) < 2:
            return jsonify({'error': 'El nombre debe tener al menos 2 caracteres'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        if password != confirmar_password:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Crear usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({'mensaje': 'Registro exitoso. Por favor, inicia sesión'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_api():
    """Endpoint para iniciar sesión"""
    try:
        datos = request.get_json()
        email = datos.get('email', '').strip()
        password = datos.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not usuario.check_password(password):
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        
        login_user(usuario)
        return jsonify({
            'mensaje': 'Sesión iniciada correctamente',
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout_api():
    """Endpoint para cerrar sesión"""
    logout_user()
    return jsonify({'mensaje': 'Sesión cerrada correctamente'}), 200

@app.route('/api/usuario-actual', methods=['GET'])
def usuario_actual():
    """Obtener datos del usuario actual"""
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'nombre': current_user.nombre,
            'email': current_user.email,
            'autenticado': True
        }), 200
    return jsonify({'autenticado': False}), 200

# ============ RUTAS PARA ESTADÍSTICAS DE PARTIDOS ============

@app.route('/api/guardar-estadisticas', methods=['POST'])
@login_required
def guardar_estadisticas():
    """Endpoint para guardar estadísticas de un partido"""
    try:
        datos = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['rebotes', 'canastas_tiradas', 'canastas_encestadas', 'canastas_3_encestadas', 'fecha_partido']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({'error': f'Campo requerido: {campo}'}), 400
        
        # Validar que los valores sean números enteros positivos
        try:
            rebotes = int(datos.get('rebotes', 0))
            canastas_tiradas = int(datos.get('canastas_tiradas', 0))
            canastas_encestadas = int(datos.get('canastas_encestadas', 0))
            canastas_3_encestadas = int(datos.get('canastas_3_encestadas', 0))
            
            if any(x < 0 for x in [rebotes, canastas_tiradas, canastas_encestadas, canastas_3_encestadas]):
                return jsonify({'error': 'Los valores no pueden ser negativos'}), 400
            
            # Validar que canastas_encestadas no sea mayor a canastas_tiradas
            if canastas_encestadas > canastas_tiradas:
                return jsonify({'error': 'Canastas encestadas no puede ser mayor a canastas tiradas'}), 400
            
            # Validar que canastas_3_encestadas no sea mayor a canastas_encestadas
            if canastas_3_encestadas > canastas_encestadas:
                return jsonify({'error': 'Canastas de 3 no puede ser mayor a canastas encestadas'}), 400
            
        except ValueError:
            return jsonify({'error': 'Todos los valores deben ser números enteros'}), 400
        
        # Parsear fecha
        try:
            fecha_partido = datetime.strptime(datos.get('fecha_partido'), '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        # Crear registro de estadísticas
        estadistica = EstadisticasPartido(
            usuario_id=current_user.id,
            rebotes=rebotes,
            canastas_tiradas=canastas_tiradas,
            canastas_encestadas=canastas_encestadas,
            canastas_3_encestadas=canastas_3_encestadas,
            fecha_partido=fecha_partido,
            notas=datos.get('notas', '')
        )
        
        db.session.add(estadistica)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Estadísticas guardadas correctamente',
            'estadistica': estadistica.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mis-estadisticas', methods=['GET'])
@login_required
def mis_estadisticas():
    """Endpoint para obtener las estadísticas del usuario actual"""
    try:
        # Obtener parámetros de paginación
        pagina = request.args.get('pagina', default=1, type=int)
        items_por_pagina = request.args.get('items_por_pagina', default=10, type=int)
        
        # Validar parámetros
        if pagina < 1:
            pagina = 1
        if items_por_pagina < 1 or items_por_pagina > 100:
            items_por_pagina = 10
        
        # Obtener estadísticas ordenadas por fecha descendente
        query = EstadisticasPartido.query.filter_by(usuario_id=current_user.id).order_by(EstadisticasPartido.fecha_partido.desc())
        
        total_registros = query.count()
        total_paginas = (total_registros + items_por_pagina - 1) // items_por_pagina
        
        if pagina > total_paginas and total_paginas > 0:
            pagina = total_paginas
        
        # Aplicar paginación
        estadisticas = query.offset((pagina - 1) * items_por_pagina).limit(items_por_pagina).all()
        
        # Calcular estadísticas promedio
        todas_las_estadisticas = EstadisticasPartido.query.filter_by(usuario_id=current_user.id).all()
        if todas_las_estadisticas:
            promedio_rebotes = sum(e.rebotes for e in todas_las_estadisticas) / len(todas_las_estadisticas)
            promedio_canastas_encestadas = sum(e.canastas_encestadas for e in todas_las_estadisticas) / len(todas_las_estadisticas)
            promedio_canastas_3 = sum(e.canastas_3_encestadas for e in todas_las_estadisticas) / len(todas_las_estadisticas)
            porcentaje_acierto = (sum(e.canastas_encestadas for e in todas_las_estadisticas) / sum(e.canastas_tiradas for e in todas_las_estadisticas) * 100) if sum(e.canastas_tiradas for e in todas_las_estadisticas) > 0 else 0
        else:
            promedio_rebotes = promedio_canastas_encestadas = promedio_canastas_3 = porcentaje_acierto = 0
        
        return jsonify({
            'estadisticas': [e.to_dict() for e in estadisticas],
            'total_registros': total_registros,
            'pagina_actual': pagina,
            'total_paginas': total_paginas,
            'promedios': {
                'rebotes': round(promedio_rebotes, 2),
                'canastas_encestadas': round(promedio_canastas_encestadas, 2),
                'canastas_3': round(promedio_canastas_3, 2),
                'porcentaje_acierto': round(porcentaje_acierto, 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estadistica/<int:estadistica_id>', methods=['DELETE'])
@login_required
def eliminar_estadistica(estadistica_id):
    """Endpoint para eliminar una estadística"""
    try:
        estadistica = EstadisticasPartido.query.get(estadistica_id)
        
        if not estadistica:
            return jsonify({'error': 'Estadística no encontrada'}), 404
        
        # Verificar que pertenece al usuario actual
        if estadistica.usuario_id != current_user.id:
            return jsonify({'error': 'No tienes permiso para eliminar esta estadística'}), 403
        
        db.session.delete(estadistica)
        db.session.commit()
        
        return jsonify({'mensaje': 'Estadística eliminada correctamente'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)