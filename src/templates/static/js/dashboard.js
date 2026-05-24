const dashboardConfig = window.dashboardConfig || {};
const anosDisponibles = dashboardConfig.anosDisponibles || [];
let anoActual = dashboardConfig.anoInicial;
let paginaActual = 1;
let paginaActualMetricas = 1;
const ITEMS_POR_PAGINA = 20;
const ITEMS_METRICAS_POR_PAGINA = 20;

document.addEventListener('DOMContentLoaded', () => {
    actualizarFiltros();
    generarGraficos();
    
    // Agregar listener a los tabs para mostrar/ocultar filtro
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(e) {
            const targetId = e.target.getAttribute('data-bs-target');
            const filterCard = document.getElementById('filterCard');
            
            if (targetId === '#pestana-mis-estadisticas') {
                filterCard.style.display = 'none';
            } else {
                filterCard.style.display = 'block';
            }
        });
    });
});

function actualizarFiltros() {
    anoActual = parseInt(document.getElementById('selectorAno').value, 10);
    paginaActual = 1;
    paginaActualMetricas = 1;
    cargarDatos(1);
    cargarMetricasAvanzadas(1);
    generarGraficos();
}

function cargarDatos(pagina) {
    fetch(`/api/datos-jugadores?ano=${anoActual}&pagina=${pagina}&items_por_pagina=${ITEMS_POR_PAGINA}`)
        .then(validarRespuesta)
        .then(data => mostrarDatos(data, pagina))
        .catch(error => {
            console.error('Error al cargar datos:', error);
            alert('Error al cargar los datos. Por favor, intenta nuevamente.');
        });
}

function mostrarDatos(data, pagina) {
    paginaActual = pagina;
    document.getElementById('totalJugadores').textContent = data.total_jugadores;
    document.getElementById('paginaActual').textContent = pagina;
    document.getElementById('totalPaginas').textContent = data.total_paginas;

    const tbody = document.getElementById('cuerpoTabla');
    tbody.innerHTML = '';

    if (data.datos.length === 0) {
        tbody.appendChild(crearFilaVacia(6));
    } else {
        data.datos.forEach(fila => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${fila.Jugador}</td>
                <td>${fila.Equipo}</td>
                <td class="text-center">${Math.round(fila['Partidos Jugados'])}</td>
                <td class="text-center">${Math.round(fila['Canastas Tiradas'])}</td>
                <td class="text-center">${Math.round(fila.Encestadas)}</td>
                <td class="text-center">${Math.round(fila['3 Puntos'])}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    generarPaginacion(data.total_paginas, pagina, 'paginacion', 'cargarDatos');
}

function cargarMetricasAvanzadas(pagina) {
    fetch(`/api/metricas-avanzadas?ano=${anoActual}&pagina=${pagina}&items_por_pagina=${ITEMS_METRICAS_POR_PAGINA}`)
        .then(validarRespuesta)
        .then(data => mostrarMetricasAvanzadas(data, pagina))
        .catch(error => {
            console.error('Error al cargar metricas:', error);
        });
}

function mostrarMetricasAvanzadas(data, pagina) {
    paginaActualMetricas = pagina;
    document.getElementById('totalJugadoresMetricas').textContent = data.total_jugadores;
    document.getElementById('paginaActualMetricas').textContent = pagina;
    document.getElementById('totalPaginasMetricas').textContent = data.total_paginas;

    const tbody = document.getElementById('cuerpoTablaMestricas');
    tbody.innerHTML = '';

    if (data.datos.length === 0) {
        tbody.appendChild(crearFilaVacia(10));
    } else {
        data.datos.forEach(fila => {
            const tcPercent = fila['TC%'];
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${fila.Jugador}</strong></td>
                <td>${fila.Equipo}</td>
                <td class="text-center">${Math.round(fila['Partidos Jugados'])}</td>
                <td class="text-center">${Math.round(fila['Canastas Tiradas'])}</td>
                <td class="text-center">${Math.round(fila.Encestadas)}</td>
                <td class="text-center">${Math.round(fila['3 Puntos'])}</td>
                <td class="text-center"><span class="metric-badge ${obtenerClaseTc(tcPercent)}">${fila['TC%']}%</span></td>
                <td class="text-center">${fila['2P%']}%</td>
                <td class="text-center"><span class="metric-ppp">${fila.PPP}</span></td>
                <td class="text-center">${fila['Vol. Tiro/Partido']}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    generarPaginacion(data.total_paginas, pagina, 'paginacionMetricas', 'cargarMetricasAvanzadas');
}

function generarGraficos() {
    const cargando = document.getElementById('cargandoGraficos');
    cargando.style.display = 'inline-flex';

    fetch(`/api/generar-graficos?ano=${anoActual}`)
        .then(validarRespuesta)
        .then(data => {
            mostrarGrafico('iframeScatter', 'scatterContainer', 'placeholderScatter', data.scatter_plot);
            mostrarGrafico('iframeBarras', 'barrasContainer', 'placeholderBarras', data.grafico_equipos);
            cargando.style.display = 'none';
        })
        .catch(error => {
            console.error('Error al generar graficos:', error);
            alert('Error al generar los graficos.');
            cargando.style.display = 'none';
        });
}

function generarPaginacion(totalPaginas, paginaActual, idPaginacion, funcionCambio) {
    const paginacion = document.getElementById(idPaginacion);
    paginacion.innerHTML = '';

    paginacion.appendChild(crearItemPaginacion('Anterior', paginaActual - 1, funcionCambio, paginaActual === 1));

    const inicio = Math.max(1, paginaActual - 2);
    const fin = Math.min(totalPaginas, paginaActual + 2);

    if (inicio > 1) {
        paginacion.appendChild(crearItemPaginacion('1', 1, funcionCambio));
        if (inicio > 2) {
            paginacion.appendChild(crearItemPuntos());
        }
    }

    for (let i = inicio; i <= fin; i++) {
        paginacion.appendChild(crearItemPaginacion(i, i, funcionCambio, false, i === paginaActual));
    }

    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) {
            paginacion.appendChild(crearItemPuntos());
        }
        paginacion.appendChild(crearItemPaginacion(totalPaginas, totalPaginas, funcionCambio));
    }

    paginacion.appendChild(crearItemPaginacion('Siguiente', paginaActual + 1, funcionCambio, paginaActual === totalPaginas));
}

function cambiarPagina(nuevaPagina) {
    if (nuevaPagina > 0) {
        cargarDatos(nuevaPagina);
    }
}

function validarRespuesta(response) {
    if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
    }
    return response.json();
}

function crearFilaVacia(columnas) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="${columnas}" class="text-center text-muted py-4">No hay datos disponibles</td>`;
    return tr;
}

function obtenerClaseTc(tcPercent) {
    if (tcPercent > 50) return 'metric-badge--high';
    if (tcPercent > 40) return 'metric-badge--medium';
    return 'metric-badge--low';
}

function mostrarGrafico(idIframe, idContenedor, idPlaceholder, ruta) {
    const iframe = document.getElementById(idIframe);
    iframe.src = `/${ruta}?${new Date().getTime()}`;
    document.getElementById(idContenedor).style.display = 'block';
    document.getElementById(idPlaceholder).style.display = 'none';
}

function crearItemPaginacion(texto, pagina, funcionCambio, deshabilitado = false, activo = false) {
    const li = document.createElement('li');
    li.className = `page-item ${deshabilitado ? 'disabled' : ''} ${activo ? 'active' : ''}`;
    li.innerHTML = `<a class="page-link" href="#" onclick="${funcionCambio}(${pagina}); return false;">${texto}</a>`;
    return li;
}

function crearItemPuntos() {
    const li = document.createElement('li');
    li.className = 'page-item disabled';
    li.innerHTML = '<span class="page-link">...</span>';
    return li;
}

// ============ FUNCIONES PARA ESTADÍSTICAS DE PARTIDOS ============

let paginaActualEstadisticas = 1;
const ITEMS_ESTADISTICAS_POR_PAGINA = 10;

// Inicializar estadísticas cuando el usuario se autentica
document.addEventListener('DOMContentLoaded', () => {
    verificarYMostrarPestanaEstadisticas();
    
    // Agregar listener al formulario de estadísticas
    const formCargarEstadisticas = document.getElementById('formCargarEstadisticas');
    if (formCargarEstadisticas) {
        formCargarEstadisticas.addEventListener('submit', manejarCargarEstadisticas);
    }
});

// Verificar si el usuario está autenticado y mostrar la pestaña de estadísticas
async function verificarYMostrarPestanaEstadisticas() {
    try {
        const response = await fetch('/api/usuario-actual');
        const data = await response.json();
        
        if (data.autenticado) {
            // Mostrar pestaña de estadísticas
            document.getElementById('pestana-mis-estadisticas-item').style.display = 'block';
            
            // Cargar estadísticas automáticamente
            cargarMisEstadisticas();
        }
    } catch (error) {
        console.error('Error al verificar usuario:', error);
    }
}

// Manejar el envío del formulario de estadísticas
async function manejarCargarEstadisticas(event) {
    event.preventDefault();
    
    const formMessage = document.getElementById('formMessage');
    formMessage.style.display = 'none';
    
    const datos = {
        rebotes: parseInt(document.getElementById('rebotes').value),
        canastas_tiradas: parseInt(document.getElementById('canastastairadas').value),
        canastas_encestadas: parseInt(document.getElementById('canastasencestadas').value),
        canastas_3_encestadas: parseInt(document.getElementById('canastas3encestadas').value),
        fecha_partido: document.getElementById('fechaPartido').value,
        notas: document.getElementById('notas').value
    };
    
    try {
        const response = await fetch('/api/guardar-estadisticas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const resultado = await response.json();
        
        if (!response.ok) {
            mostrarMensajeFormulario(resultado.error, 'error');
            return;
        }
        
        mostrarMensajeFormulario('¡Estadísticas guardadas correctamente!', 'success');
        document.getElementById('formCargarEstadisticas').reset();
        
        // Establecer la fecha de hoy por defecto
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('fechaPartido').value = hoy;
        
        // Recargar la tabla de estadísticas
        setTimeout(() => {
            cargarMisEstadisticas();
        }, 1000);
        
    } catch (error) {
        mostrarMensajeFormulario('Error al guardar las estadísticas: ' + error.message, 'error');
    }
}

// Mostrar mensaje en el formulario
function mostrarMensajeFormulario(mensaje, tipo) {
    const formMessage = document.getElementById('formMessage');
    formMessage.textContent = mensaje;
    formMessage.className = `message-box ${tipo}`;
    formMessage.style.display = 'block';
    
    if (tipo === 'success') {
        setTimeout(() => {
            formMessage.style.display = 'none';
        }, 3000);
    }
}

// Cargar estadísticas del usuario
async function cargarMisEstadisticas(pagina = 1) {
    try {
        const response = await fetch(`/api/mis-estadisticas?pagina=${pagina}&items_por_pagina=${ITEMS_ESTADISTICAS_POR_PAGINA}`);
        const data = await response.json();
        
        if (!response.ok) {
            console.error('Error al cargar estadísticas:', data.error);
            return;
        }
        
        mostrarMisEstadisticas(data, pagina);
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// Mostrar estadísticas cargadas
function mostrarMisEstadisticas(data, pagina) {
    paginaActualEstadisticas = pagina;
    
    const promediosContainer = document.getElementById('promediosContainer');
    const estadisticasTablaContainer = document.getElementById('estadisticasTablaContainer');
    const sinDatosContainer = document.getElementById('sinDatosContainer');
    const paginacionContainer = document.getElementById('paginacionContainer');
    
    if (data.estadisticas.length === 0) {
        promediosContainer.style.display = 'none';
        estadisticasTablaContainer.style.display = 'none';
        sinDatosContainer.style.display = 'block';
        paginacionContainer.style.display = 'none';
        return;
    }
    
    // Mostrar promedios
    document.getElementById('promedioRebotes').textContent = data.promedios.rebotes.toFixed(2);
    document.getElementById('promedioCanastas').textContent = data.promedios.canastas_encestadas.toFixed(2);
    document.getElementById('promedioTriples').textContent = data.promedios.canastas_3.toFixed(2);
    document.getElementById('porcentajeAcierto').textContent = data.promedios.porcentaje_acierto.toFixed(2) + '%';
    promediosContainer.style.display = 'grid';
    
    // Llenar tabla
    const tbody = document.getElementById('estadisticasTableBody');
    tbody.innerHTML = '';
    
    data.estadisticas.forEach(estadistica => {
        const tr = document.createElement('tr');
        const porcentajeAcierto = estadistica.canastas_tiradas > 0 
            ? ((estadistica.canastas_encestadas / estadistica.canastas_tiradas) * 100).toFixed(1)
            : 0;
        
        tr.innerHTML = `
            <td>${new Date(estadistica.fecha_partido).toLocaleDateString('es-ES')}</td>
            <td class="text-center"><strong>${estadistica.rebotes}</strong></td>
            <td class="text-center">${estadistica.canastas_tiradas}</td>
            <td class="text-center">${estadistica.canastas_encestadas}</td>
            <td class="text-center">${estadistica.canastas_3_encestadas}</td>
            <td><small>${estadistica.notas || '-'}</small></td>
            <td class="text-center">
                <button class="btn-eliminar" onclick="eliminarEstadistica(${estadistica.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    estadisticasTablaContainer.style.display = 'block';
    sinDatosContainer.style.display = 'none';
    
    // Mostrar paginación si es necesario
    if (data.total_paginas > 1) {
        document.getElementById('paginacionInfo').textContent = `Página ${pagina} de ${data.total_paginas}`;
        
        const btnAnterior = document.getElementById('btnAnterior');
        const btnSiguiente = document.getElementById('btnSiguiente');
        
        btnAnterior.style.display = pagina > 1 ? 'block' : 'none';
        btnSiguiente.style.display = pagina < data.total_paginas ? 'block' : 'none';
        
        btnAnterior.value = pagina;
        btnSiguiente.value = pagina;
        
        paginacionContainer.style.display = 'flex';
    } else {
        paginacionContainer.style.display = 'none';
    }
}

// Cambiar página de estadísticas
function cargarPaginaEstadisticas(pagina) {
    if (pagina > 0) {
        cargarMisEstadisticas(pagina);
    }
}

// Eliminar estadística
async function eliminarEstadistica(estadisticaId) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta estadística?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/estadistica/${estadisticaId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const data = await response.json();
            alert('Error: ' + data.error);
            return;
        }
        
        // Recargar estadísticas
        cargarMisEstadisticas(paginaActualEstadisticas);
        
    } catch (error) {
        console.error('Error al eliminar estadística:', error);
        alert('Error al eliminar la estadística');
    }
}

// Establecer la fecha de hoy por defecto al cargar el formulario
document.addEventListener('DOMContentLoaded', () => {
    const fechaInput = document.getElementById('fechaPartido');
    if (fechaInput) {
        const hoy = new Date().toISOString().split('T')[0];
        fechaInput.value = hoy;
    }
});

