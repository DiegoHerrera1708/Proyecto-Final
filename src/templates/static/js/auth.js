// Funciones para abrir/cerrar modal
function abrirLoginModal() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function cerrarLoginModal(event) {
    // Si se hace clic en el overlay, cierra el modal
    if (event && event.target.id !== 'loginModal') return;
    
    const modal = document.getElementById('loginModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    
    // Limpiar formularios y errores
    limpiarFormularios();
}

function limpiarFormularios() {
    document.getElementById('formLogin').reset();
    document.getElementById('formRegistro').reset();
    document.getElementById('loginError').textContent = '';
    document.getElementById('registroError').textContent = '';
    document.getElementById('loginError').classList.remove('show');
    document.getElementById('registroError').classList.remove('show');
}

// Cambiar entre pestañas
function cambiarARegistro(e) {
    e.preventDefault();
    document.getElementById('loginTab').style.display = 'none';
    document.getElementById('registroTab').style.display = 'block';
}

function cambiarALogin(e) {
    e.preventDefault();
    document.getElementById('loginTab').style.display = 'block';
    document.getElementById('registroTab').style.display = 'none';
}

// Mostrar mensaje de error
function mostrarError(elementId, mensaje) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = mensaje;
    errorElement.classList.add('show');
    errorElement.style.display = 'block';
}

function limpiarError(elementId) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = '';
    errorElement.classList.remove('show');
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    limpiarError('loginError');
    
    const email = document.getElementById('emailLogin').value;
    const password = document.getElementById('passwordLogin').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            mostrarError('loginError', data.error || 'Error al iniciar sesión');
            return;
        }
        
        // Actualizar UI
        actualizarUIUsuario(data.usuario);
        cerrarLoginModal();
        
    } catch (error) {
        mostrarError('loginError', 'Error de conexión: ' + error.message);
    }
}

// Handle Registro
async function handleRegistro(event) {
    event.preventDefault();
    limpiarError('registroError');
    
    const nombre = document.getElementById('nombreRegistro').value;
    const email = document.getElementById('emailRegistro').value;
    const password = document.getElementById('passwordRegistro').value;
    const confirmar_password = document.getElementById('confirmarPassword').value;
    
    try {
        const response = await fetch('/api/registrarse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre, email, password, confirmar_password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            mostrarError('registroError', data.error || 'Error al registrarse');
            return;
        }
        
        // Mostrar mensaje de éxito
        const successMsg = document.createElement('div');
        successMsg.className = 'success-message show';
        successMsg.textContent = data.mensaje;
        document.getElementById('registroTab').appendChild(successMsg);
        
        // Limpiar formulario y cambiar a login después de 2 segundos
        setTimeout(() => {
            document.getElementById('formRegistro').reset();
            cambiarALogin({preventDefault: () => {}});
        }, 2000);
        
    } catch (error) {
        mostrarError('registroError', 'Error de conexión: ' + error.message);
    }
}

// Cerrar sesión
async function cerrarSesion() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Actualizar UI
            document.getElementById('btnLogin').style.display = 'block';
            document.getElementById('userMenu').style.display = 'none';
            window.location.reload();
        }
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
    }
}

// Actualizar UI cuando usuario inicia sesión
function actualizarUIUsuario(usuario) {
    const btnLogin = document.getElementById('btnLogin');
    const userMenu = document.getElementById('userMenu');
    const usuarioNombre = document.getElementById('usuarioNombre');
    
    btnLogin.style.display = 'none';
    userMenu.style.display = 'flex';
    usuarioNombre.textContent = usuario.nombre;
    
    // Mostrar pestaña de estadísticas para usuario logueado
    if (typeof verificarYMostrarPestanaEstadisticas === 'function') {
        verificarYMostrarPestanaEstadisticas();
    }
}

// Verificar si el usuario ya está autenticado al cargar la página
async function verificarAutenticacion() {
    try {
        const response = await fetch('/api/usuario-actual');
        const data = await response.json();
        
        if (data.autenticado) {
            actualizarUIUsuario({
                nombre: data.nombre,
                email: data.email,
                id: data.id
            });
        }
    } catch (error) {
        console.error('Error al verificar autenticación:', error);
    }
}

// Ejecutar verificación al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    verificarAutenticacion();
    
    // Cerrar modal al presionar Escape
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            const modal = document.getElementById('loginModal');
            if (modal.classList.contains('active')) {
                cerrarLoginModal();
            }
        }
    });
});
