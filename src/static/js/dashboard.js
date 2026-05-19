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

