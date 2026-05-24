import pytest

from main import app
from database import db
from models import Usuario


@pytest.fixture
def cliente():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        yield cliente


@pytest.fixture
def usuario_prueba():
    email = "login_test@example.com"

    with app.app_context():
        Usuario.query.filter_by(email=email).delete()

        usuario = Usuario(nombre="Usuario Login", email=email)
        usuario.set_password("password123")

        db.session.add(usuario)
        db.session.commit()

        yield usuario

        Usuario.query.filter_by(email=email).delete()
        db.session.commit()


@pytest.mark.parametrize("datos", [
    {},
    {"email": "login_test@example.com"},
    {"password": "password123"},
])
def test_login_requiere_email_y_password(cliente, datos):
    respuesta = cliente.post("/api/login", json=datos)
    cuerpo = respuesta.get_json()

    assert respuesta.status_code == 400
    assert cuerpo["error"] == "Email y contraseña requeridos"


def test_login_falla_con_password_incorrecta(cliente, usuario_prueba):
    respuesta = cliente.post("/api/login", json={
        "email": usuario_prueba.email,
        "password": "password_mal",
    })
    cuerpo = respuesta.get_json()

    assert respuesta.status_code == 401
    assert cuerpo["error"] == "Email o contraseña incorrectos"


def test_login_correcto_devuelve_usuario(cliente, usuario_prueba):
    respuesta = cliente.post("/api/login", json={
        "email": usuario_prueba.email,
        "password": "password123",
    })
    cuerpo = respuesta.get_json()

    assert respuesta.status_code == 200
    assert cuerpo["mensaje"] == "Sesión iniciada correctamente"
    assert cuerpo["usuario"]["nombre"] == "Usuario Login"
    assert cuerpo["usuario"]["email"] == usuario_prueba.email


def test_usuario_actual_esta_autenticado_despues_del_login(cliente, usuario_prueba):
    cliente.post("/api/login", json={
        "email": usuario_prueba.email,
        "password": "password123",
    })

    respuesta = cliente.get("/api/usuario-actual")
    cuerpo = respuesta.get_json()

    assert respuesta.status_code == 200
    assert cuerpo["autenticado"] is True
    assert cuerpo["email"] == usuario_prueba.email
