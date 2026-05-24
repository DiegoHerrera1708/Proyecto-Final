from models import Jugador, Persona, Usuario


def test_jugador_hereda_de_persona():
    jugador = Jugador(
        nombre="Pau Gasol",
        equipo="Lakers",
        posicion="Pivot",
        dorsal=16,
        altura_cm=213,
        peso_kg=113,
    )

    assert isinstance(jugador, Persona)
    assert jugador.nombre == "Pau Gasol"
    assert jugador.equipo == "Lakers"


def test_jugador_to_dict_incluye_datos_basicos_y_deportivos():
    jugador = Jugador(nombre="Ricky Rubio", equipo="Cavaliers", posicion="Base")
    datos = jugador.to_dict()

    assert datos["nombre"] == "Ricky Rubio"
    assert datos["equipo"] == "Cavaliers"
    assert datos["posicion"] == "Base"


def test_usuario_hereda_de_persona():
    usuario = Usuario(nombre="Usuario Test", email="usuario@test.com")

    assert isinstance(usuario, Persona)
    assert usuario.nombre == "Usuario Test"
    assert usuario.email == "usuario@test.com"
