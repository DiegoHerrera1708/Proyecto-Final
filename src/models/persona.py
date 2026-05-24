from datetime import datetime

from database import db


class Persona(db.Model):
    """Clase base abstracta para modelos con datos personales comunes."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def datos_basicos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M")
            if self.fecha_creacion
            else None,
        }
