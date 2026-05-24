from .persona import Persona
from database import db


class Jugador(Persona):
    """Modelo de jugador que hereda los datos comunes de Persona."""

    __tablename__ = "jugador"

    equipo = db.Column(db.String(80), nullable=False)
    posicion = db.Column(db.String(40), nullable=True)
    dorsal = db.Column(db.Integer, nullable=True)
    altura_cm = db.Column(db.Integer, nullable=True)
    peso_kg = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        datos = self.datos_basicos()
        datos.update({
            "equipo": self.equipo,
            "posicion": self.posicion,
            "dorsal": self.dorsal,
            "altura_cm": self.altura_cm,
            "peso_kg": self.peso_kg,
        })
        return datos

    def __repr__(self):
        return f"<Jugador {self.nombre} - {self.equipo}>"
