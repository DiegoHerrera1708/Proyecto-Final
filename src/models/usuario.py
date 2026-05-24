from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from .persona import Persona


class Usuario(UserMixin, Persona):
    """Modelo de Usuario para autenticacion."""

    __tablename__ = "usuario"

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    estadisticas = db.relationship(
        "EstadisticasPartido",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        """Hashear y guardar la contrasena."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verificar la contrasena."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Usuario {self.email}>"


class EstadisticasPartido(db.Model):
    """Modelo para guardar estadisticas de partidos de usuarios."""

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    rebotes = db.Column(db.Integer, nullable=False, default=0)
    canastas_tiradas = db.Column(db.Integer, nullable=False, default=0)
    canastas_encestadas = db.Column(db.Integer, nullable=False, default=0)
    canastas_3_encestadas = db.Column(db.Integer, nullable=False, default=0)

    fecha_partido = db.Column(db.DateTime, nullable=False)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            "id": self.id,
            "rebotes": self.rebotes,
            "canastas_tiradas": self.canastas_tiradas,
            "canastas_encestadas": self.canastas_encestadas,
            "canastas_3_encestadas": self.canastas_3_encestadas,
            "fecha_partido": self.fecha_partido.strftime("%Y-%m-%d %H:%M"),
            "notas": self.notas,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
        }

    def __repr__(self):
        return f"<EstadisticasPartido {self.usuario_id} - {self.fecha_partido}>"
